class Extract(object):
    def __init__(self):
        self.value = 5

    def parse_data(self,filename:str):
        return {}

    def get_init_questions(self):
        return []

    def set_init_questions(self,questions:dict):
        return

    def display_name(self):
        pass

    def get_extractors(self):
        result = []
        for sc in Extract.__subclasses__():
            result.append(sc()) #instantiate
        # [cls.__name__ for cls in Extract.__subclasses__()]
        return result

class Travis(Extract):
    init_questions = {}

    def display_name(self):
        return 'Travis Lab'

    def get_init_questions(self):
        result = []
        result.append("Experiment Name (Blank for none): ")
        return result

    def set_init_questions(self,questions:dict):
        self.init_questions = questions

    def parse_data(self,filename:str):
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

        if self.init_questions.con

        return result