from flask import Flask, render_template,request
from program import getname
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('screen.html')
@app.route('/action',methods=['GET', 'POST'])
def action():

    if request.method == 'POST':
        print(request.form['name'])
        output = getname(request.form['name'])
        return render_template('screen2.html',data = output[0].to_html(), data2= output[1].to_html())

if __name__ == '__main__':
    app.run(debug=True)
