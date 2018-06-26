import argparse
import os
import json
import random
import time

import http.server # import BaseHTTPRequestHandler, HTTPServer
import flask

ui_html = '''
<html lang="en">
	<head>
		<title>prostoboxes</title>
		<script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>
	</head>
	<body>
		<svg preserveAspectRatio="none" viewBox="0 0 1 1" style="position: absolute; width: 100%; height: 100%;" height="100%" width="100%" xmlns="http://www.w3.org/2000/svg">
			<image preserveAspectRatio="none" height="1" width="1"> 
			<rect stroke-width="0.03" fill-opacity="0.5" style="display:none" />
			<circle r="0.008" style="display:none" />
		</svg>
		<script type="text/javascript">
			var boxes = [];
			var imagename = '';

			function next()
			{
				$
					.post({ url : '/' + imagename, contentType : 'application/json', data : JSON.stringify(boxes) })
					.done(function(imagename_new) {
						$('image').attr('href', '/' + imagename_new);
						$('svg circle:not([style=display\\\\:none])').remove();
						$('svg rect:not([style=display\\\\:none])').remove();
						boxes = [];
						imagename = imagename_new;
					}); 
			}

			function add(cx, cy)
			{
				if(boxes.length == 0 || boxes.slice().pop().length == 4)
					boxes.push([]);

				var box = boxes.slice().pop();
				box.push(cx);
				box.push(cy);

				var color = 'hsl(' + (360.0 * (boxes.length % 8) / 8) + ', 50%, 50%)';
				$('svg').append($('svg circle[style=display\\\\:none]').clone().removeAttr('style').attr("cx", cx).attr("cy", cy).attr("fill", color));
				if(box.length == 4)
					$('svg').append($('svg rect[style=display\\\\:none]').clone().removeAttr('style').attr("x", box[0]).attr("y", box[1]).attr("fill", color).attr("width", box[2] - box[0]).attr("height", box[3] - box[1]));
					
				//var cmp_convex_hull = function(a, b) { return (a.x - center.x) * (b.y - center.y) - (b.x - center.x) * (a.y - center.y); };
				//this.events[this.events.length - 1].value.sort(cmp_convex_hull);
			}

			function remove()
			{
				var box = boxes.slice().pop() || [];

				if(box.length == 4)
				{
					box.splice(-2, 2);
					$('svg circle').last().remove();
					$('svg rect').last().remove();
				}
				else if(box.length == 2)
				{
					boxes.pop();
					$('svg circle').last().remove();
				}
			}

			$('svg').click(function(ev)
			{
				var x = (ev.pageX - $(this).offset().left) / $(this).width(), y = (ev.pageY - $(this).offset().top) / $(this).height();
				add(x, y);
			});

			$(document).keydown(function(ev)
			{
				if(ev.keyCode == 32)
					next();
				else if(ev.keyCode == 46)
					remove();
			});

			next();
		</script>
	</body>
</html>
'''

parser = argparse.ArgumentParser()
parser.add_argument('--images', default = 'images')
parser.add_argument('--db', default = 'db')
parser.add_argument('--seed', default = time.time(), type = int)
parser.add_argument('--port', default = 5000, type = int)
args = parser.parse_args()

for dir in [args.images, args.db]:
	if not os.path.exists(dir):
		os.makedirs(dir)
random.seed(args.seed)

app = flask.Flask(__name__, static_url_path = '')
@app.route('/', defaults = dict(filename = None), methods = ['GET', 'POST'])
@app.route('/<filename>', methods = ['GET', 'POST'])
def handle(filename):
	if flask.request.method == 'GET':
		return flask.send_from_directory(os.path.join(os.getcwd(), args.images), filename) if filename else ui_html
	if filename:
		with open(os.path.join(args.db, filename), 'w') as f:
			json.dump(flask.request.get_json(), f)
	return random.choice(list(set(os.listdir(args.images)) - set(os.listdir(args.db))) or ['DONE'])
app.run()

class BoundingBoxAnnotationUI(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_POST(self):
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

try:
	server = http.server.HTTPServer(('', args.port), BoundingBoxAnnotationUI)
	server.serve_forever()
except:
	server.socket.close()
