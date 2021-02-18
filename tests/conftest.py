import pytest 

@pytest.fixture 
def normalized_temp_string():
    return "AQW00061705 01 01   804P   803C   801C   799C   797C\
           797C   796C   808C   833C   844C   850C   856C   858C   857C\
                  857C   854C   849C   843C   835C   824C   817C   813C   809C   808C"