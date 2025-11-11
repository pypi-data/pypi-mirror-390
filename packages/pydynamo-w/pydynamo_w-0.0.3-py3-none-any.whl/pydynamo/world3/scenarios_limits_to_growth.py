scenarios = [
    {
        'title': 'Scenario #1: Business as usual',
        'changes': {}
    },

    {
        'title': 'Scenario #2: double -- and more accessible -- non-renewable resources',
        'changes': {
            'fcaortm': 2002,
            'nri': 2000000000000.0,
            'fcaor2t': [1.0, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        }
    },

    {
        'title': 'Scenario #3: Scenario #2 plus pollution technology advancing from 2002',
        'changes': {
            'pyear': 2002,
            'pptcmt': [-0.04, 0],
            'fcaortm': 2002,
            'nri': 2000000000000.0,
            'fcaor2t': [1.0, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        }
    },

    {
        'title': 'Scenario #4: Scenario #3 plus yield technology advancing from 2002',
        'changes': {
            'pyear': 2002,
            'lytcrmt': [0, 0.04],
            'pptcmt': [-0.04, 0],
            'fcaortm': 2002,
            'nri': 2000000000000.0,
            'fcaor2t': [1.0, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        }
    },

    {
        'title': 'Scenario #5: Scenario #4 plus erosion control advancing from 2002',
        'changes': {
            'fcaortm': 2002,
            'lytcrmt': [0, 0.04],
            'llmytm': 2002,
            'fcaor2t': [1.0, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            'pyear': 2002,
            'nri': 2000000000000.0,
            'pptcmt': [-0.04, 0]
        }
    },
    
    {
        'title': 'Scenario #6: Scenario #5 plus resource technology advancing from 2002',
        'changes': {
            'fcaortm': 2002,
            'lytcrmt': [0, 0.04],
            'llmytm': 2002,
            'fcaor2t': [1.0, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            'rtcmt': [0.04, 0.0],
            'pyear': 2002,
            'nri': 2000000000000.0,
            'pptcmt': [-0.04, 0],
            'pyear': 2002,
        }
    },

    {
        'title': 'Scenario #7: is Scenario #2 plus population policies from 2002',
        'changes': {
            'zpgt': 2002,
            'fcest': 2002,
            'nri': 2000000000000.0,
        }
    },

    {
        'title': 'Scenario #8: Scenario #7 plus a fixed goal for industrial output per capita from 2002, and 25 % longer life of capital',
        'changes': {
            'iopcd': 350,
            'fcest': 2002,
            'iet': 2002,
            'alsc2': 25,
            'alai2': 2.5,
            'alic2': 18,
            'pyear': 2002,
            'nri': 2000000000000.0,
            'zpgt': 2002
        }
    },

    {
        'title': 'Scenario #9: Scenario #8 \nplus resource -, pollution -, and yield – technologies\n and erosion control advancing from 2002',
        'changes': {
            'lytcrmt': [0, 0.04],
            'llmytm': 2002,
            'iopcd': 350,
            'fcest': 2002,
            'iet': 2002,
            'rtcmt': [0.04, 0.0],
            'alsc2': 25,
            'alai2': 2.5,
            'alic2': 18,
            'pyear': 2002,
            'nri': 2000000000000.0,
            'pptcmt': [-0.04, 0],
            'zpgt': 2002
        }
    },

    {
        'title': 'Scenario #10: Scenario #9 with policy implementation 20 years earlier, in 1982',
        'changes': {
            'lytcrmt': [0, 0.04],
            'llmytm': 1982,
            'iopcd': 350,
            'fcest': 2002,
            'iet': 1982,
            'rtcmt': [0.04, 0.0],
            'alsc2': 25,
            'alai2': 2.5,
            'alic2': 18,
            'pyear': 1982,
            'nri': 2000000000000.0,
            'pptcmt': [-0.04, 0],
            'zpgt': 2002
        }
    },

    {
        'title': 'Scenario #11: Scenario #9 with policy implementation 10 years later, in 2012:',
        'changes': {
            'lytcrmt': [0, 0.04],
            'llmytm': 2012,
            'iopcd': 350,
            'fcest': 2002,
            'iet': 2012,
            'rtcmt': [0.04, 0.0],
            'alsc2': 25,
            'alai2': 2.5,
            'alic2': 18,
            'pyear': 2012,
            'nri': 2000000000000.0,
            'pptcmt': [-0.04, 0],
            'zpgt': 2002
        }
    }
]

fils = [[1, 2, 3, 4, 5], [2, 7, 8, 9], [9, 10], [9, 11]]

obs = [
    "À mesure que les ressources s'épuisent, une part beaucoup plus grande des investissements industriels doit être alouée à leur extraction, et les investissements deviennent alors insuffisants, ce qui enclenche la boucle de rétroaction d'effondrement du capital industriel.",
    "La pollution générée par l'agriculture",
]
    
