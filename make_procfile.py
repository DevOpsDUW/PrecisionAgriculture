# make_procfile.py
with open('Procfile', 'w') as f:
    f.write('web: cd src/web_app && python app.py')
print("Procfile created successfully!")