from . import mimiciv_text_sectionizer
from . import notes_embedding
from . import icd_cohort_combined_searching
import pandas as pd

class Note:
    path: str
    nlp: str
    sec: str
    embedding : bool
    regex_icd: str

    def __init__(self, path, sec, nlp=None, embedding=False, regex_icd=None):
        self.path =path
        self.nlp = nlp
        self.sec = sec
        self.embedding = embedding
        self.regex_icd = regex_icd

    def search(self):
        '''
        Pass in a regex command of ICDs to search in diagnoses

        Returns
        -------
        DataFrame: Each patients diagnoses. 
        
        '''
        if not self.regex_icd:
            raise ValueError('No Regex command passed into class instance of MIMIC NLP. mimiciv_note(path, nlp, sec, embedding, regex_icd)')
        cohort = icd_cohort_combined_searching.icd_combined_search(self.regex_icd)
        return cohort

    def sectionize(self):
        '''
        Sectionize based off note type: Discharge, Radiology.

        The following sections for each note type
        -----------------------------------------
        
        Discharge: Chief Complaint, Major Procedures, History of Present Illness, Review of Systems, Past Medical History, Past Surgical History, Social History, Family History, Physical Exam, Discharge Physical Exam, Pertinent Results, Labs on Admission, Labs on Discharge, Microbiology, Diagnostic Paracentesis, Imaging, Hospital Course, Transitional Issues, Medications on Admission, Discharge Medications, Discharge Disposition, Discharge Diagnosis, Discharge Condition, Discharge Instructions, Follow-up

        Radiology: Exam, Indication, Comparison, Technique, Findings, Impression, Addendum
        

        Returns
        -------
        DataFrame: Sectionized note.
        '''
        print('MIMIC Sectionizer will take a while...')
        df = pd.read_csv(self.path)
        print('Opened MIMIC Note.')
        if self.regex_icd:
            cohort = search()
            subject_ids = cohort['subject_id'].unique()
            subject_ids = [int(x) for x in subject_ids]
            df = df[df['subject_id'].isin(subject_id)]
        if self.nlp == 'Sectionize':
            return mimiciv_text_sectionizer.extract_data_sectionizer(df, self.sec)
        return df

    def embedding(df):
        '''
        Generates embeddings for the notes.

        Returns
        -------
        DataFrame: Embedded notes
        '''
        if not self.embedding:
            raise ValueError('Did not pass True for embedding into class instance of MIMIC NLP. mimiciv_note(path, nlp, sec, embedding, regex_icd')
        return notes_embedding.get_embedding(df)
        
            
            
        
            
        
        

    
            
            
            
    
        
        
        
        
    