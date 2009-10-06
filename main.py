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

def all_strategies(file_path):
  return re.match("OpenLayers/Strategy/\w+\.js", file_path) > -1

def all_protocols(file_path):
  return re.match("OpenLayers/Protocol/\w+\.js", file_path) > -1

def all_popups(file_path):
  return re.match("OpenLayers/Popup/\w+\.js", file_path) > -1

def all_filters(file_path):
  return re.match("OpenLayers/Filter/\w+\.js", file_path) > -1

def filename_to_sourcefile(file_path):
  content = open('openlayers_src/trunk/lib/' + file_path, "U").read() # TODO: Ensure end of line @ EOF?
  return mergejs.SourceFile(file_path, content) # TODO: Chop path?
  

class MainHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    release_28 = mergejs.scanjs('openlayers_src/release-2.8/lib')
    trunk = mergejs.scanjs('openlayers_src/trunk/lib')
    trunk = [
        { 'type': 'layer', 'name': 'Layer Types',
          'options': map(filename_to_sourcefile, filter(all_layers, trunk))},
        { 'type': 'control', 'name': 'Controls',
          'options': map(filename_to_sourcefile, filter(all_controls, trunk))},
        { 'type': 'language', 'name': 'Languages',
          'options': map(filename_to_sourcefile, filter(all_languages, trunk))},
        { 'type': 'format', 'name': 'Formats',
          'options': map(filename_to_sourcefile, filter(all_formats, trunk))},
        { 'type': 'strategy', 'name': 'Strategies',
          'options':  map(filename_to_sourcefile, filter(all_strategies, trunk))},
        { 'type': 'protocol', 'name': 'Protocols',
          'options': map(filename_to_sourcefile, filter(all_protocols, trunk))},
        { 'type': 'popup', 'name': 'Popups',
          'options': map(filename_to_sourcefile, filter(all_popups, trunk))},
        { 'type': 'filter', 'name': 'Filters',
          'options': map(filename_to_sourcefile, filter(all_filters, trunk))},
        ]
    release_28 = [
        { 'type': 'layer', 'name': 'Layer Types',
          'options': map(filename_to_sourcefile, filter(all_layers, release_28))},
        { 'type': 'control', 'name': 'Controls',
          'options': map(filename_to_sourcefile, filter(all_controls, release_28))},
        { 'type': 'language', 'name': 'Languages',
          'options': map(filename_to_sourcefile, filter(all_languages, release_28))},
        { 'type': 'format', 'name': 'Formats',
          'options': map(filename_to_sourcefile, filter(all_formats, release_28))},
        { 'type': 'strategy', 'name': 'Strategies',
          'options':  map(filename_to_sourcefile, filter(all_strategies, release_28))},
        { 'type': 'protocol', 'name': 'Protocols',
          'options': map(filename_to_sourcefile, filter(all_protocols, release_28))},
        { 'type': 'popup', 'name': 'Popups',
          'options': map(filename_to_sourcefile, filter(all_popups, release_28))},
        { 'type': 'filter', 'name': 'Filters',
          'options': map(filename_to_sourcefile, filter(all_filters, release_28))},
        ]

    template_values = {
        'trunk': trunk, 'release_28': release_28}
    self.response.out.write(template.render(path, template_values))

class OpenLayerer(webapp.RequestHandler):
  def post(self):
    # TODO: bounds checking
    layers = self.request.get_all('layer')
    controls = self.request.get_all('control')
    languages = self.request.get_all('language')
    formats = self.request.get_all('format')
    strategies = self.request.get_all('strategy')
    protocols = self.request.get_all('protocol')
    filters = self.request.get_all('filter')
    popups = self.request.get_all('popup')
    version = self.request.get('version')


    forceFirst = first
    include = controls + layers + languages + strategies \
        + protocols + formats + popup + filter
    config = mergejs.Config(include=include, forceFirst=forceFirst)

    try:
        merged = mergejs.merge('openlayers_src/%s/lib' % version, config)
    except:
        self.response.out.write("An error occurred. Currently a single layer, language, or control must be selected, OpenLayerer does not do empty builds yet.")
        return
        
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
