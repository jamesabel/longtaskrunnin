
from .__version__ import application_name, author
from .rmdir import rmdir
from .e_info import EInfo
from .communication import EInfoInterprocessCommunication, write_e_info, get_interprocess_communication_file_path
from .longtaskrunnin import LongTaskRunnin, options_str
