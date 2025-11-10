
import re 
import os
import json
import glob
from datetime import date

from pathlib import Path

from . import constant

from .nextflow_building_blocks import Nextflow_Building_Blocks
from .outils import *
from .bioflowinsighterror import BioFlowInsightError





class Nextflow_File(Nextflow_Building_Blocks):
    def __init__(self, address, workflow, first_file  = False):
        self.address = address 
        self.workflow = workflow
        self.first_file = first_file
        self.main = None
        self.workflow.add_nextflow_file_2_workflow(self)
        self.includes = []
        self.processes = []
        self.subworkflows = []
        self.functions = []
        self.initialised = False
        self.added_2_rocrate = False
        contents = check_file_exists(self.get_file_address(), self)
        Nextflow_Building_Blocks.__init__(self, contents, initialise_code=True)
        self.check_file_correctness()

    #----------------------
    #GENERAL
    #----------------------

    def get_link_dico_processes(self):
        return self.workflow.get_link_dico_processes()

    def get_cycle_status(self):
        return self.workflow.get_cycle_status()

    def add_to_ternary_operation_dico(self, old, new):
        self.workflow.add_to_ternary_operation_dico(old, new)
    
    def add_map_element(self, old, new):
        self.workflow.add_map_element(old, new)

    def get_root_directory(self):
        return self.workflow.get_root_directory()

    def get_string_line(self, bit_of_code):
        return self.code.get_string_line(bit_of_code)

    def get_conditions_2_ignore(self):
        return self.workflow.get_conditions_2_ignore()

    #Method that returns the address of the file
    def get_file_address(self, short = False):
        if(not short):
            return Path(os.path.normpath(self.address))
        else:
            return str(self.get_file_address())[len(self.workflow.get_workflow_directory())+1:]
    

    def get_nextflow_file(self):
        return self
    
    def get_DSL(self):
        return self.workflow.get_DSL()
    


    #def get_origin(self):
    #    return self.workflow
    
    def check_file_correctness(self):
        code = self.get_code()
        #if(code.count("{")!=code.count("}")):
        #    curly_count = get_curly_count(code)
        #    if(curly_count!=0):
        #        raise BioFlowInsightError("ntsnocif", self)
        #if(code.count("(")!=code.count(")")):
        #    parenthese_count = get_parenthese_count(code)
        #    if(parenthese_count!=0):
        #        raise BioFlowInsightError("ntsnopif", self)

        if(code.count('"""')%2!=0):
            raise BioFlowInsightError("onotqif", self)

        


    #Method which returns the DSL of the workflow -> by default it's DSL2
    #I use the presence of include, subworkflows and into/from in processes as a proxy
    def find_DSL(self):
        DSL = "DSL2"
        #If there are include
        pattern = constant.FULL_INLCUDE_2
        for match in re.finditer(pattern, self.get_code()):
            return DSL
        #If there are subworkflows
        for match in re.finditer(constant.SUBWORKFLOW_HEADER, self.get_code()):
            return DSL
        #If there is the main
        for match in re.finditer(constant.WORKFLOW_HEADER_2, '\n'+self.get_code()+'\n'):
            return DSL
        #Analyse the processes
        self.extract_processes()
        for p in self.processes:
            DSL = p.which_DSL()
            if(DSL=="DSL1"):
                self.processes = []
                return DSL
        self.processes = []
        return DSL
    
    def get_workflow(self):
        return self.workflow
    
    def get_duplicate_status(self):
        return self.workflow.get_duplicate_status()
    
    #Returns either a subworkflow or process from the name
    def get_element_from_name(self, name):
        for process in self.processes:
            if(name==process.get_alias()):
                return process
        for subworkflow in self.subworkflows:
            if(name==subworkflow.get_alias()):
                return subworkflow
        for fun in self.functions:
            if(name==fun.get_alias()):
                return fun
        raise BioFlowInsightError("estbdic", self, name)

    def get_modules_defined(self):
        return self.get_processes()+self.get_subworkflows()+self.get_functions()+self.get_modules_included()

    def get_output_dir(self):
        return self.workflow.get_output_dir()

    #----------------------
    #PROCESSES
    #----------------------
    def extract_processes(self):
        from .process import Process
        code = self.get_code()
        #Find pattern
        for match in re.finditer(constant.PROCESS_HEADER, code):
            start = match.span(0)[0]
            name = match.group(1)
            try:
                end = extract_curly(code, match.span(0)[1])#This function is defined in the functions file
            except:
                raise BioFlowInsightError('uteeoe', self, "process", name)
            p = Process(code=code[start:end], nextflow_file=self)
            self.processes.append(p)

    def get_processes(self):
        return self.processes


    #----------------------
    #SUBWORKFLOW (ones found in the file)
    #----------------------
    def extract_subworkflows(self):
        from .subworkflow import Subworkflow
        #Get code without comments
        code = self.get_code()
        #Find pattern
        for match in re.finditer(constant.SUBWORKFLOW_HEADER, code):
            start = match.span(0)[0]
            name = match.group(1)
            try:
                end = extract_curly(code, match.span(0)[1])#This function is defined in the functions file
            except:
                raise BioFlowInsightError('uteeoe', self, "subworkflow", name)
            sub = Subworkflow(code=code[start:end], nextflow_file=self, name=match.group(1))
            self.subworkflows.append(sub)

    def get_subworkflows(self):
        return self.subworkflows

    #----------------------
    #MAIN WORKFLOW
    #----------------------
    #This method extracts the "main" workflow from the file 
    def extract_main(self):
        if(self.first_file):
            from .main import Main
            #This returns the code without the comments
            code = "\n"+self.get_code()+"\n"
            #Find pattern
            twice = False
            for match in re.finditer(constant.WORKFLOW_HEADER_2, code):
                
                start = match.span(1)[0]
                end = extract_curly(code, match.span(1)[1])#This function is defined in the functions file
                self.main = Main(code= code[start:end], nextflow_file=self)
                if(twice):
                    raise BioFlowInsightError('mmic', self)
                twice = True
            if(self.main==None):
                self.main = Main(code= "", nextflow_file=self)
                #raise BioFlowInsightError("nomic", self)


    #----------------------
    #FUNCTIONS
    #----------------------

    #Method that extracts the functions from a file -> we don't analyse them
    #since they don't structurally change the workflow
    def extract_functions(self):
        from .function import Function
        #pattern_function = r"(def|String|void|Void|byte|short|int|long|float|double|char|Boolean) *(\w+) *\([^,)]*(,[^,)]+)*\)\s*{"
        pattern_function = constant.HEADER_FUNCTION
        code = self.get_code()
        #Find pattern
        for match in re.finditer(pattern_function, code):
            start = match.span(0)[0]
            if(match.group(2) not in ['if']):
                try:
                    end = extract_curly(code, match.span(0)[1])#This function is defined in the functions file
                    f = Function(code = code[start:end], name = match.group(2), origin =self)
                except:
                        #Since in reality we don't do anything with the groups -> so need to analyse them
                        f = Function(code = match.group(0), name = match.group(2), origin =self)
                        #f = Function(code = code[start:end], name = match.group(2), origin =self)
                self.functions.append(f)
            #    print(code)
            #    1/0
            #f = Code(code=code[start:end], origin=self)
            #Fobiden names of functions
            

    def get_functions(self):
        return self.functions


    #----------------------
    #INCLUDES
    #----------------------
    def extract_includes(self):
        from .include import Include

        code = self.get_code()
        pattern = constant.FULL_INLCUDE_2
        
        for match in re.finditer(pattern, code):
            
            includes = match.group(1).replace('{', '').replace('}', '').strip()

            #We do this if there are multiple includes
            #TODO -> this in a nicer way
            #To take into account
            #include {
            #PAIRTOOLS_SELECT
            #    as PAIRTOOLS_SELECT_VP;
            #PAIRTOOLS_SELECT
            #    as PAIRTOOLS_SELECT_LONG
            found_semi, found_n = bool(includes.find(";")+1), bool(includes.find("\n")+1)
            if(found_semi and found_n):
                temp = includes.split(";")
                tab = []
                for temp_include in temp:
                    temp_include = temp_include.replace("\n", ' ').strip()
                    if(temp_include[:3] in constant.LIST_AS):
                        tab[-1] = tab[-1]+" "+temp_include
                    else:
                        tab.append(temp_include)
                includes = tab
            elif(found_semi):
                includes = includes.split(";")
            elif(found_n):
                temp = includes.split("\n")
                tab = []
                for temp_include in temp:
                    temp_include = temp_include.strip()
                    if(temp_include[:3]in constant.LIST_AS):
                        tab[-1] = tab[-1]+" "+temp_include
                    else:
                        tab.append(temp_include)
                includes = tab
            else:
                includes = [includes]
            
            
            #TODO -> check this
            #https://www.nextflow.io/docs/latest/plugins.html#plugins
            #https://github.com/nextflow-io/nf-validation
            #address = match.group(0).split('from')[1].strip()
            address = match.group(6).strip()
            if(address[1:].split('/')[0] not in ['plugin']):
                include = Include(code =match.group(0), file = address, importing = includes, nextflow_file=self)
                self.includes.append(include)

    def get_includes(self):
        return self.includes
    
    def get_modules_included(self):
        modules = []
        for include in self.includes:
            modules+=list(include.defines.values())
        return modules

    def get_calls_made_outside_of_main(self):
        #Code without processes
        code = self.get_code()
        for proecess in self.processes:
            temp = code
            code = code.replace(proecess.get_code(), "")
            if(temp==code):
                raise Exception("This souldn't happen")
        for sub in self.subworkflows:
            temp = code
            code = code.replace(sub.get_code(), "")
            if(temp==code):
                raise Exception("This souldn't happen")
        for fun in self.functions:
            temp = code
            code = code.replace(fun.get_code(), "")
            if(temp==code):
                raise Exception("This souldn't happen")
        if(self.first_file and self.main!=None):
            temp = code
            code = code.replace(self.main.get_code(), "")
            if(temp==code):
                raise Exception("This souldn't happen")
        for include in self.includes:
            temp = code
            code = code.replace(include.get_code(), "")
            if(temp==code):
                raise Exception("This souldn't happen")

        from .root import Root
        self.root = Root(code=code, origin= self, modules_defined=self.get_modules_defined(), subworkflow_inputs = [])
        self.root.initialise()
        calls = {}
        self.root.get_all_calls_in_subworkflow(calls=calls)
        return list(calls.keys())

    #----------------------
    #INITIALISE
    #----------------------

    #Method that initialises the nextflow file
    def initialise(self):
        #If the file is not alreday initialised then we self.initialise it
        if(not self.initialised):
            self.initialised = True
            if(self.workflow.get_display_info_bool()):
                print(f"Analysing -> '{self.get_file_address()}'")
        
            if(self.get_DSL()=="DSL2"):

                #Extarct Processes
                self.extract_processes()
                #Analysing Processes
                for process in self.processes:
                    process.initialise()

                #Code without processes
                code = self.get_code()
                for proecess in self.processes:
                    temp = code
                    code = code.replace(proecess.get_code(), "", 1)
                    if(temp==code):
                        print(f"'{code}'")
                        print(proecess.get_code())
                        raise Exception("This souldn't happen")
                    
                
                #Extract includes
                self.extract_includes()

                #Extract subworkflows
                self.extract_subworkflows()

                #Analyse Inludes
                for include in self.includes:
                    include.initialise()

                #Extract main
                self.extract_main()
                

                #Extract functions
                self.extract_functions()

                #Analyse Main
                if(self.first_file and self.main!=None):
                    self.main.initialise()
                #
                ##Analyse subworkflows
                #indice=1
                #for sub in self.subworkflows:
                #    sub.initialise()
                #    indice+=1
            elif(self.get_DSL()=="DSL1"):
                from .main import Main
                #Extarct Processes
                self.extract_processes()
                code = self.get_code()
                #Extract functions
                self.extract_functions()

                
                #Replacing the processes and functions defined with their identifiers -> this is to simplifly the analysis with the conditions
                for process in self.processes:
                    temp = code
                    code = code.replace(process.get_code(get_OG = True), f"process: {str(process)}")
                    if(temp==code):
                        print(process.get_code())
                        raise Exception("Something went wrong the code hasn't changed")
             
                for function in self.functions:
                    temp = code
                    code = code.replace(function.get_code(get_OG = True), f"function: {str(function)}")
                    #if(temp==code):
                    #    #print(code)
                    #    #print("-", function.get_code(get_OG = True))
                    #    #print(self.functions)
                    #    raise Exception("Something went wrong the code hasn't changed")
                self.main = Main(code= code, nextflow_file=self)
                self.main.initialise()
                
            else:
                raise Exception("This shouldn't happen")
        
    def add_to_has_part(self, dico, to_add_key):
        file_name = str(self.get_file_address())[len(dico["temp_directory"]):]
        file_dico = get_dico_from_tab_from_id(dico, file_name)
        file_dico["hasPart"].append({"@id":to_add_key})

    
    def add_computational_workflow_to_types(self, dico):
        file_name = str(self.get_file_address())[len(dico["temp_directory"]):]
        file_dico = get_dico_from_tab_from_id(dico, file_name)
        file_dico["@type"].append("ComputationalWorkflow")

    def get_file_rocrate_key(self, dico):
        file_name = str(self.get_file_address())[len(dico["temp_directory"]):]
        return file_name
