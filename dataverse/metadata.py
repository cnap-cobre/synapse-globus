import os
class Metadata(object):
    
    def extract(self,filename:str):
        return {}

    def get_init_questions(self):
        return []

    def set_init_questions(self,questions:dict):
        return

    def display_name(self):
        return "N/A"

    def id_num(self):
        #This should NEVER CHANGE in Subclasses! It's what the user
        #chooses via script to select the lab number
        return 0

    def get_extractors(self):
        result = {}
        for sc in Metadata.__subclasses__():
            instance = sc()
            result[instance.id_num()] = instance
        # [cls.__name__ for cls in Extract.__subclasses__()]
        result[self.id_num()] = self
        return result

class Travis(Metadata):
    EXPERIMENT_NAME = "Experiment Name (Blank for none): "
    init_questions = {}

    def display_name(self):
        return 'Travis Lab'

    def id_num(self):
        #This should NEVER CHANGE in Subclasses! It's what the user
        #chooses via script to select the lab number
        return 1

    def get_init_questions(self):
        result = []
        result.append(self.EXPERIMENT_NAME)
        return result

    def set_init_questions(self,questions:dict):
        self.init_questions = questions

    def extract(self,filepath:str):
        filename = os.path.basename(filepath)
        #Check to see if filename matches format gb104847.111:
        #   gb: refers to the experiment name (we progress down the alphabet, gb, gc, gd, etc...)
        #   1: refers to squad (we have 24 testing chambers and more than 24 rats and so they get
        #       ran in different squads at different times of the day).  Recently, we've kept this
        #       at 1 regardless of squad because the identifier hasn't been necessary.
        #   048: refers to a batch number assigned to group of rats when they arrive (if we
        #       transfer rats to another study, they'd keep their same batch number but get
        #       different experiment numbers).
        #   47: refers to the subject ID (starting at '01' for the first rat in a given batch
        #   111: after the period refers to the session number.
        if len(filename) != 12: return
        if filename[8] != '.': return
        try:
            session = int(filename[9:])
        except ValueError:
             return
        
        result = {}
        result['experiment'] = filename[0:1]
        result['squad'] = filename[2:3]
        result['batch'] = filename[3:6]
        result['subject_id'] = filename[6:8]
        result['session'] = session

        if self.EXPERIMENT_NAME in self.init_questions:
            result['experiment'] = self.init_questions[self.EXPERIMENT_NAME]

        return result