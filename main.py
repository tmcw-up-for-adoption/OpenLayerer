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

import wsgiref.handlers, os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import build, mergejs

layers = [
  'ArcGIS93Rest',
  'ArcIMS',
  'Boxes',
  'EventPane',
  'FixedZoomLevels',
  'GML',
  'GeoRSS',
  'Google',
  'Grid',
  'HTTPRequest',
  'Image',
  'KaMap',
  'KaMapCache',
  'MapGuide',
  'MapServer',
  'Markers',
  'MultiMap',
  'PointTrack',
  'SphericalMercator',
  'TMS',
  'Text',
  'Vector',
  'VirtualEarth',
  'WFS',
  'WMS',
  'WorldWind',
  'XYZ',
  'Yahoo']

controls = [
  'ArgParser',
  'Attribution',
  'Button',
  'DragFeature',
  'DragPan',
  'DrawFeature',
  'EditingToolbar',
  'GetFeature',
  'KeyboardDefaults',
  'LayerSwitcher',
  'Measure',
  'ModifyFeature',
  'MouseDefaults',
  'MousePosition',
  'MouseToolbar',
  'NavToolbar',
  'Navigation',
  'NavigationHistory',
  'OverviewMap',
  'Pan',
  'PanPanel',
  'PanZoom',
  'PanZoomBar',
  'Panel',
  'Permalink',
  'Scale',
  'ScaleLine',
  'SelectFeature',
  'Snapping',
  'Split',
  'WMSGetFeatureInfo',
  'ZoomBox',
  'ZoomIn',
  'ZoomOut',
  'ZoomPanel',
  'ZoomToMaxExtent']

languages = [
  'ar',
  'be-tarask',
  'ca',
  'cs-CZ',
  'da-DK',
  'de',
  'en-CA',
  'en',
  'es',
  'fi',
  'fr',
  'gl',
  'gsw',
  'hsb',
  'ia',
  'io',
  'is',
  'it',
  'ja',
  'km',
  'ksh',
  'nb',
  'nl',
  'nn',
  'no',
  'oc',
  'pt-BR',
  'pt',
  'ru',
  'sk',
  'sv-SE',
  'te',
  'vi',
  'zh-CN',
  'zh-TW']

first = [
  'OpenLayers/SingleFile.js',
  'OpenLayers.js',
  'OpenLayers/BaseTypes.js',
  'OpenLayers/BaseTypes/Class.js',
  'OpenLayers/Util.js']
      

class MainHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    template_values = {
        'layers': layers,
        'controls': controls,
        'languages': languages}
    self.response.out.write(template.render(path, template_values))

class OpenLayerer(webapp.RequestHandler):
  def post(self):
    layers = self.request.get_all('layer')
    controls = self.request.get_all('control')
    languages = self.request.get_all('language')
    control_list = ['OpenLayers/Control/%s.js' % i for i in controls]
    layer_list = ['OpenLayers/Layer/%s.js' % i for i in layers]
    language_list = ['OpenLayers/Lang/%s.js' % i for i in languages]
    forceFirst = first
    include = control_list + layer_list + language_list

    config = mergejs.Config(include=include, forceFirst=forceFirst)

    # TODO: obviously fix this
    merged = mergejs.merge('openlayers_src/trunk/lib', config)

    # TODO: allow uncompressed output
    output = build.minimize(merged)

    # TODO: move
    license = file('license.txt').read() 

    # Force client to download file
    self.response.headers['Content-Type'] = 'application/octet-stream'
    self.response.headers['Content-Disposition'] = 'attachment; filename="OpenLayers.js"'
    self.response.out.write(license + output)

def main():
  application = webapp.WSGIApplication([('/', MainHandler), ('/openlayerer', OpenLayerer)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
