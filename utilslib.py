# --------------------------------------------------------------------------
# Blendyn -- file utilslib.py
# Copyright (C) 2015 -- 2020 Andrea Zanoni -- andrea.zanoni@polimi.it
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of Blendyn, add-on script for Blender.
#
#    Blendyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Blendyn  is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Blendyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

import bpy

import logging

from mathutils import *
from math import *
from bpy.types import Operator
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import csv

class BLENDYN_OT_load_section(bpy.types.Operator, ImportHelper):
    """ Loads profile to assign to curve bevel, in Selig format """
    bl_idname = "blendyn.load_section"
    bl_label = "Load NACA profile in Selig format"

    filter_glob: bpy.props.StringProperty(
        default = "*.*",
        options = {'HIDDEN'},
        )

    def execute(self, context):
        try:
            scol = bpy.data.collections['sections']
            set_active_collection('sections')
            with open(self.filepath, 'r') as sf:     
                reader = csv.reader(sf, delimiter=' ', skipinitialspace=True)
                name = next(reader)
                cvdata = bpy.data.curves.new(' '.join(name), 'CURVE')
                cvdata.dimensions = '2D'

                # if the curve already exists, Blender changes the name of the newly created one
                name = cvdata.name
                poly = cvdata.splines.new('POLY')

                # first point
                row = next(reader)
                poly.points[0].co = Vector(( float(row[0]), float(row[1]), 0.0, 0.0 ))

                # other points
                for row in reader:
                    poly.points.add(1)
                    poly.points[-1].co = Vector(( float(row[0]), float(row[1]), 0.0, 0.0 ))

                obj = bpy.data.objects.new(name, cvdata)
                scol.objects.link(obj)
             
                for item in bpy.context.scene.objects:
                    if item.select_get():
                        try:
                            item.data.bevel_object = obj
                        except AttributeError:
                            pass

                return {'FINISHED'}
        except IOError:
            message = "BLENDYN_OT_load_section::execute(): "\
                    + "Could not locate the selected file"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
        except StopIteration:
            message = "BLENDYN_OT_load_section::execute(): "\
                    + "Unespected end of file"
            self.report({'WARNING'}, message)
            logging.warning(message)
            return {'CANCELLED'}
        except KeyError:
            message = "BLENDYN_OT_load_section::execute(): "\
                    + "Could not finde 'sections' collection"
            self.report({'ERROR'}, message)
            logging.error(message)
            return {'CANCELLED'}
# -----------------------------------------------------------
# end of fmin function BLENDYN_OT_load_section class


## Utility functions
def fmin(x):
    min = x[0]
    loc = 0
    for idx in range(1, len(x)):
        if x[idx] < min:
            min = x[idx]
            loc = idx
    return (min, loc)
# -----------------------------------------------------------
# end of fmin function

def fmax(x):
    max = x[0]
    loc = 0
    for idx in range(1, len(x)):
        if x[idx] > max:
            max = x[idx]
            loc = idx
    return (max, loc)
# -----------------------------------------------------------
# end of fmax function

def parse_rotmat(rw, idx, R): 
    R[0][0] = float(rw[idx])
    R[0][1] = float(rw[idx + 1])
    R[0][2] = float(rw[idx + 2])
    R[1][0] = float(rw[idx + 3])
    R[1][1] = float(rw[idx + 4])
    R[1][2] = float(rw[idx + 5])
    R[2][0] = float(rw[idx + 6])
    R[2][1] = float(rw[idx + 7])
    R[2][2] = float(rw[idx + 8])
    pass

def parenting(child, parent):
    bpy.context.view_layer.objects.active = child
    bpy.ops.object.constraint_add(type='CHILD_OF')
    child.constraints["Child Of"].target = parent

    child.constraints["Child Of"].use_scale_x = False
    child.constraints["Child Of"].use_scale_y = False
    child.constraints["Child Of"].use_scale_z = False

# -----------------------------------------------------------
# end of parenting function


def eldbmsg(msg, who, elem):
    # Prints various standard debug messages for element import.

    def parse(whomsg):
       message = whomsg + "Parsing " + elem.type \
               + " " + str(elem.int_label)
       logging.info(message)
       return message

    def foundid(whomsg):
        message = whomsg \
                + "found existing entry in elements dictionary for "\
                + elem.type + " " + str(elem.int_label) + ". Updating it."
        logging.info(message)
        return message

    def notfoundid(whomsg):
        message = whomsg \
                + "didn't find entry in elements dictionary for "\
                + "{0} {1}. Creating it.".format(elem.type, elem.int_label)
        logging.info(message)
        return message

    def objexists(whomsg):
        message = whomsg \
                + "Element " + elem.type + " " + str(elem.int_label) \
                + " is already imported. Remove the Blender object "\
                + "or rename it before re-importing the element."
        logging.error(message)
        return message

    def objsnotfound(whomsg):
        message = whomsg \
                + "Could not find Blender objects"
        logging.error(message)
        return message

    def n1notfound(whomsg):
        message = whomsg \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[0].int_label)
        logging.error(message)
        return message 

    def n2notfound(whomsg):
        message = whomsg \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[1].int_label)
        logging.error(message)
        return message 

    def n3notfound(whomsg):
        message = whomsg \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[2].int_label)
        logging.error(message)
        return message 

    def n4notfound(whomsg):
        message = whomsg \
                + "Could not find the Blender object associated to node " + \
                str(elem.nodes[3].int_label)
        logging.error(message)
        return message 
    
    def libraryerror(whomsg):
        message = whomsg \
                + "Could not import " \
                + elem.type + " " + str(elem.int_label) \
                + ": could not load library object"
        logging.error(message)
        return message

    def collerror(whomsg):
        message = whomsg \
                + "Cannot find the container collection for "\
                + "element " + elem.type + " " + str(elem.int_label)
        logging.error(message)
        return message

    def dicterror(whomsg):
        message = whomsg \
                + "Element " + elem.type + " " + str(elem.int_label) + " " \
                + "not found."
        logging.error(message)
        return message

    def importsuccess(whomsg):
        message = whomsg \
                + "Element " + elem.type + " " + str(elem.int_label) + " " \
                + "imported correcly."
        logging.info(message)
        return message

    # map messages
    messages = {'PARSE_ELEM' : parse,
                'FOUND_DICT' : foundid,
                'NOTFOUND_DICT' : notfoundid,
                'OBJECT_EXISTS' : objexists,
                'OBJECTS_NOTFOUND' : objsnotfound,
                'NODE1_NOTFOUND' : n1notfound,
                'NODE2_NOTFOUND' : n2notfound,
                'NODE3_NOTFOUND' : n3notfound,
                'NODE4_NOTFOUND' : n4notfound,
                'LIBRARY_ERROR' : libraryerror,
                'DICT_ERROR' : dicterror,
                'IMPORT_SUCCESS' : importsuccess,
                'COLLECTION_ERROR' : collerror
    }

    whomsg = who + ": "
    message = messages[msg.pop()](whomsg)
    print(message)

def recur_layer_collection(layer_collection, coll_name):
    """ Recursively traverse layer collection for coll_name """
    found = None
    if (layer_collection.name == coll_name):
        return layer_collection
    for layer in layer_collection.children:
        found = recur_layer_collection(layer, coll_name)
        if found:
            return found
# -----------------------------------------------------------
# end of recur_layer_collection function

def cquat(q):
    """ resets to zero small components of quaternion,
        to avoid flickering """
    tol = 1e-6
    q.x = q.x*(abs(q.x) < tol)
    q.y = q.y*(abs(q.y) < tol)
    q.z = q.z*(abs(q.z) < tol)
    return q

def set_active_collection(coll_name):
    """ Changes the active collection to coll_name after searching
        for it with recur_layer_collection() """
    curr_layer_collection = bpy.context.view_layer.layer_collection
    new_layer_collection = recur_layer_collection(curr_layer_collection, coll_name)
    bpy.context.view_layer.active_layer_collection = new_layer_collection
# -----------------------------------------------------------
# end of set_active_collection function

def outline_toggle(context, action):
    area = next(a for a in context.screen.areas if a.type == 'OUTLINER')
    bpy.ops.outliner.show_hierarchy({'area': area}, 'INVOKE_DEFAULT')
    state = {'expand': 1, 'collapse': 2}
    for i in range(state[action]):
        bpy.ops.outliner.expanded_toggle({'area': area})
        area.tag_redraw()
# -----------------------------------------------------------
# end of outline_toggl() function
# source: https://blenderartists.org/t/question-regarding-expanding-collapsing-collection-in-outliner-in-2-8/1175242
# NOTE: right now, not used by anyone! Should be called at the end of
#       entities import, but UI is not refreshed! FIXME
