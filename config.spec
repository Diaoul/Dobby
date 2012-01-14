[General]
welcome_message = string(default='I am ready to serve you, master.')
failed_message = string(default='I did not understand.')
confirmation_messages = string_list(default=list('Yes?', 'Yes, master?', 'What can I do for you?'))
recognition_timeout = integer(0, 60, default=5)

[Logging]
file = string(default='dobby.log')
max_bytes = integer(default=2097152)
backup_count = integer(0, 3, default=3)

[Speaker]
speaker = option('speechdispatcher', default='speechdispatcher')

[[SpeechDispatcher]]
engine = option('espeak', 'flite', default='espeak')
voice = option('MALE1', 'MALE2', 'MALE3', 'FEMALE1', 'FEMALE2', 'FEMALE3', 'CHILD_MALE', 'CHILD_FEMALE', default='MALE1')
language = option('en', 'fr', default='en')
volume = integer(-100, 100, default=100)
rate = integer(-100, 100, default=0)
pitch = integer(-100, 100, default=0)

[Recognizer]
recognizer = option('julius', default='julius')

[[Julius]]
host = string(default='localhost')
port = integer(0, default=10500)
encoding = string(default='utf-8')
min_score = float(0, default=3000.0)

[Trigger]
triggers = option_list('clapper', 'julius', default=list('julius'))

[[Clapper]]
device_index = integer(0, 20, default=8)
block_time = float(0, 2, default=0.1)

[[Julius]]
sentence = string(default='dobby')
action = boolean(default=True)