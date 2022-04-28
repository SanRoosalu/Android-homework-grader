from backend import validate, handle_post, queue
from flask import Flask, render_template, request
from datetime import datetime


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def main_site():
    if request.method == 'POST':
        print('Laeti üles fail')

        success, errorMes = validate(request)
        if not success:
            from backend import working
            queueSize = queue.qsize() + 1 if working else queue.qsize()
            errorMessage = errorMes
            return render_template('index.html', queueSize=queueSize, errorMessage=errorMessage)

        queue.put((request, datetime.now()))
        results, percent = handle_post()
        return render_template('results.html', results=results, percent=percent)
    else:
        from backend import working
        queueSize = queue.qsize() + 1 if working else queue.qsize()
        return render_template('index.html', queueSize=queueSize)


if __name__ == '__main__':
    app.run(debug=True)
