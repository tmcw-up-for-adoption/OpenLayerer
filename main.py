#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import wsgiref.handlers, os, re
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import build, mergejs
from collections import defaultdict

template.register_template_library('templatetags.options')

first = [
  'OpenLayers/SingleFile.js',
  'OpenLayers.js',
  'OpenLayers/BaseTypes.js',
  'OpenLayers/BaseTypes/Class.js',
  'OpenLayers/Util.js']
      
def all_layers(file_path):
  return re.match("OpenLayers/Layer/\w+\.js", file_path) > -1

def all_controls(file_path):
  return re.match("OpenLayers/Control/\w+\.js", file_path) > -1

def all_languages(file_path):
  return re.match("OpenLayers/Lang/\w+\.js", file_path) > -1

def all_formats(file_path):
  return re.match("OpenLayers/Format/\w+\.js", file_path) > -1

class MainHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    release_28 = mergejs.scanjs('openlayers_src/release-2.8/lib')
    trunk = mergejs.scanjs('openlayers_src/trunk/lib')
    trunk = {
        'layers': filter(all_layers, trunk),
        'controls': filter(all_controls, trunk),
        'languages': filter(all_languages, trunk),
        'formats': filter(all_formats, trunk),
        }
    release_28 = {
        'layers': filter(all_layers, release_28),
        'controls': filter(all_controls, release_28),
        'languages': filter(all_languages, release_28),
        'formats': filter(all_formats, release_28),
        }
    template_values = {
        'trunk': trunk, 'release_28': release_28}
    self.response.out.write(template.render(path, template_values))

class OpenLayerer(webapp.RequestHandler):
  def post(self):
    # TODO: bounds checking
    layers = self.request.get_all('layer')
    controls = self.request.get_all('control')
    languages = self.request.get_all('language')
    version = self.request.get('version')


    forceFirst = first
    include = controls + layers + languages
    config = mergejs.Config(include=include, forceFirst=forceFirst)

    merged = mergejs.merge('openlayers_src/%s/lib' % version, config)
    output = file('license.txt').read() + build.minimize(merged)

    # Force client to download file
    self.response.headers['Content-Type'] = 'application/octet-stream'
    self.response.headers['Content-Disposition'] = 'attachment; filename="OpenLayers.js"'
    self.response.out.write(output)

def main():
  application = webapp.WSGIApplication([('/', MainHandler), ('/openlayerer', OpenLayerer)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
