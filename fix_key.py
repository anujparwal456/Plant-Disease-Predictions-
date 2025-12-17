import re  
with open('backend/app.py', 'r') as f:  
    content = f.read()  
content = content.replace('AIzaSyCSPkavnaWhdOBpO4Co_rl7muKDZRZS_p0', '')  
with open('backend/app.py', 'w') as f:  
    f.write(content)  
