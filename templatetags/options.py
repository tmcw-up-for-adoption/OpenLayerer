from google.appengine.ext.webapp import template
import re

register = template.create_template_register()

def friendly_name(jsfile):
  matches = re.search('(\w+)\.js', jsfile)
  return matches.group(1)

def trunk_link(jsfile):
  return "http://dev.openlayers.org/docs/files/%s.html" % jsfile.replace('.', '-')

def release_28_link(jsfile):
  return "http://dev.openlayers.org/releases/OpenLayers-2.8/doc/apidocs/files/%s.html" % jsfile.replace('.', '-')



register.filter('friendly_name', friendly_name)
register.filter('trunk_link', trunk_link)
register.filter('release_28_link', release_28_link)
