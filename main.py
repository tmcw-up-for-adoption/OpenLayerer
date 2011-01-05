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

version_dir = 'openlayers_src/OpenLayers-2.9.1/lib'

first = [
  'OpenLayers/SingleFile.js',
  'OpenLayers.js',
  'OpenLayers/BaseTypes.js',
  'OpenLayers/BaseTypes/Class.js',
  'OpenLayers/Util.js',
  'OpenLayers/Renderer.js',
  'OpenLayers/Handler.js',
  'Rico/Corner.js']
  
  #  'OpenLayers/Renderer/Canvas.js',
  #'OpenLayers/Renderer/Elements.js',
  #'OpenLayers/Renderer/SVG.js',
  #'OpenLayers/Renderer/VML.js',
#  'OpenLayers/Handler.js',
      
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

def all_renderers(file_path):
  return re.match("OpenLayers/Renderer/\w+\.js", file_path) > -1

def all_protocols(file_path):
  return re.match("OpenLayers/Protocol/\w+\.js", file_path) > -1

def all_popups(file_path):
  return re.match("OpenLayers/Popup/\w+\.js", file_path) > -1

def all_filters(file_path):
  return re.match("OpenLayers/Filter/\w+\.js", file_path) > -1

def all_handlers(file_path):
  return re.match("OpenLayers/Handler/\w+\.js", file_path) > -1

def filename_to_sourcefile_release_29(file_path):
  content = open(os.path.join(version_dir, file_path), "U").read()
  return mergejs.SourceFile(file_path, content) # TODO: Chop path?

class MainHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    release_29 = mergejs.scanjs(version_dir)
    release_29 = [
        { 'type': 'layer', 'name': 'Layer Types',
          'options': map(filename_to_sourcefile_release_29, filter(all_layers, release_29))},
        { 'type': 'control', 'name': 'Controls',
          'options': map(filename_to_sourcefile_release_29, filter(all_controls, release_29))},
        { 'type': 'language', 'name': 'Languages',
          'options': map(filename_to_sourcefile_release_29, filter(all_languages, release_29))},
        { 'type': 'format', 'name': 'Formats',
          'options': map(filename_to_sourcefile_release_29, filter(all_formats, release_29))},
        { 'type': 'strategy', 'name': 'Strategies',
          'options':  map(filename_to_sourcefile_release_29, filter(all_strategies, release_29))},
        { 'type': 'protocol', 'name': 'Protocols',
          'options': map(filename_to_sourcefile_release_29, filter(all_protocols, release_29))},
        { 'type': 'renderer', 'name': 'Renderers',
          'options': map(filename_to_sourcefile_release_29, filter(all_renderers, release_29))},
        { 'type': 'popup', 'name': 'Popups',
          'options': map(filename_to_sourcefile_release_29, filter(all_popups, release_29))},
        { 'type': 'filter', 'name': 'Filters',
          'options': map(filename_to_sourcefile_release_29, filter(all_filters, release_29))},
        { 'type': 'handlers', 'name': 'Handlers',
          'options': map(filename_to_sourcefile_release_29, filter(all_handlers, release_29))},
        ]

    template_values = {
        'release_29': release_29}
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
    handlers = self.request.get_all('handler')
    popups = self.request.get_all('popup')
    renderers = self.request.get_all('renderer')
    version = self.request.get('version')

    include = controls + layers + languages + strategies \
        + protocols + formats + popups + filters + renderers + handlers

    if len(include) == 0:
        print "You didn't choose any of the things you need to build OpenLayers. Come on, choose something!"

    config = mergejs.Config(include=include, forceFirst=first)

    try:
        merged = mergejs.merge(version_dir, config)
    except Exception, e:
        print e
        self.response.out.write("An error occurred. Currently a single layer, language, or control must be selected, OpenLayerer does not do empty builds yet.")
        return

    if self.request.get("onPostBack") == "build" :
        output = file('license.txt').read() + build.minimize(merged)
    else: 
        output = include 

    # Force client to download file
    self.response.headers['Content-Type'] = 'application/octet-stream'
    if self.request.get("onPostBack") == "build" :
        self.response.headers['Content-Disposition'] = 'attachment; filename="OpenLayers.js"'
    else:
        self.response.headers['Content-Disposition'] = 'attachment; filename="OpenLayers.conf"'
    self.response.out.write(output)

def main():
  application = webapp.WSGIApplication([('/', MainHandler), ('/openlayerer', OpenLayerer)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
