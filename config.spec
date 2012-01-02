[General]
welcome_message = boolean(default=True)

[Logging]
file = string(default='dobby.log')
max_bytes = integer(default=2097152)
backup_count = integer(0, 3, default=3)

[TTS]
engine = option('espeak', 'flite', default='espeak')
voice = option('MALE1', 'MALE2', 'MALE3', 'FEMALE1', 'FEMALE2', 'FEMALE3', 'CHILD_MALE', 'CHILD_FEMALE', default='MALE1')
language = option('en', 'fr', default='en')
volume = integer(-100, 100, default=100)
rate = integer(-100, 100, default=0)
pitch = integer(-100, 100, default=0)

[Trigger]
triggers = option_list('clapper', 'dobby', default=list('clapper'))
[[Clapper]]
device_index = integer(0, 20, default=8)
block_time = float(0, 2, default=0.1)