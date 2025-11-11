
class Type:
        ENTRY = "E"
        OUT = "O"
        AUTOMATIC_PAYMENT = "AP"
        PAID_ENTRY = 'PE'

        CHOICES = (
               (ENTRY , "Entry"),
               (OUT , "Out"),
               (AUTOMATIC_PAYMENT, "Automatic Payment"),
               (PAID_ENTRY , "Paid entry")
        )


        
class RegistryClassification:
        VARIABLE = "variable"
        FIX = "fix"
        INVESTIMENT = "investiment"

        CHOICES = (
               (VARIABLE, "variable"),
               (FIX , "fix"),
               (INVESTIMENT, "investiment"),
        )


class Frequency:
        NONE = 0  
        WEEK = 7  
        BIWEEK = 15  
        MONTH = 30  
        YEAR = 365  

        CHOICES = (
               (NONE, "None"),
               (WEEK , "Week"),
               (BIWEEK, "Biweek"),
               (BIWEEK, "Biweek"),
        )

        @staticmethod
        def get_frequency(frequency: int):
            mapping = {
                Frequency.WEEK : 2,
                Frequency.BIWEEK : 3,
                Frequency.MONTH : 4,
                Frequency.YEAR : 5,
                 
            }
            return mapping.get(frequency, 1)
