from User import User
from Run import Run
from Data import Data

User.create()
Run.create()
Data.create()
id = User.add('Steve', 'Barriault', 'skidoomaniac@yahoo.com', 'vector123')
print ('user id %s created' % id)

Run.importFile(id, 'linkedin', '2022-10-01', 'LinkedIn_oct22.html.json')
#importJSON(cls, user_id, media, date_str, filename)
