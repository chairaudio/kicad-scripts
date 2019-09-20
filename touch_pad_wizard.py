#
# This program source code file is part of KiCad, a free EDA CAD application.
#
# Copyright (C) 2012-2014 KiCad Developers, see change_log.txt for contributors.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may find one here:
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# or you may search the http://www.gnu.org website for the version 2 license,
# or you may write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#

from pcbnew import *
import FootprintWizardBase
import pcbnew

class TouchPadWizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        """
        Return footprint name.
        This is specific to each footprint class, you need to implement this
        """
        return 'Touch Pad'

    def GetDescription(self):
        """
        Return footprint description.
        This is specific to each footprint class, you need to implement this
        """
        return 'Capacitive Touch Pad wizard'

    def GetValue(self):
        return "TouchPad-{s}_{x:g}x{y:g}mm".format(
            s = self.pads['rows'],
            x = pcbnew.ToMM(self.pads['columns']*self.pads['diamond_width']),
            y = pcbnew.ToMM(self.pads['rows']*self.pads['diamond_width'])
            )

    def GenerateParameterList(self):
        self.AddParam("Pads", "rows", self.uInteger, 4, min_value=2)
        self.AddParam("Pads", "columns", self.uInteger, 8, min_value=1)
        self.AddParam("Pads", "diamond_width", self.uMM, 5)
        self.AddParam("Pads", "clearance", self.uMM, 1)

    @property
    def pads(self):
        return self.parameters['Pads']

    # build a rectangular pad
    def smdRectPad(self,module,size,pos,name):
        pad = D_PAD(module)
        pad.SetSize(size)
        pad.SetShape(PAD_SHAPE_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName(name)
        pad.SetOrientation(450)
        return pad


    def smdTrianglePad(self,module,size,pos,name,up_down=1,left_right=0):
        pad = D_PAD(module)
        pad.SetSize(wxSize(size[0],size[1]))
        pad.SetShape(PAD_SHAPE_TRAPEZOID)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName(name)
        pad.SetDelta(wxSize(left_right*size[1],up_down*size[0]))
        return pad


    # This method checks the parameters provided to wizard and set errors
    def CheckParameters(self):
        #TODO - implement custom checks
        pass

    # The start pad is made of a rectangular pad plus a couple of
    # triangular pads facing tips on the middle/right of the first
    # rectangular pad
    def AddStartPad(self,position,touch_width,clearance,name):
        module = self.module
        #step_length = step_length - clearance
        size_pad = wxSize(touch_width,touch_width)
        pad = self.smdRectPad(module,size_pad,position,name)
        module.Add(pad)



    # compound a "start pad" shape plus a triangle on the left, pointing to
    # the previous touch-pad
    def AddMiddlePad(self,position,touch_width,clearance,name):
        module = self.module
        #step_length = step_length - clearance
        #size_pad = wxSize(touch_width,touch_width)

        size_pad = wxSize(touch_width,touch_width)
        pad = self.smdRectPad(module,size_pad,position,name)
        module.Add(pad)




    def AddFinalPad(self,position,touch_width,clearance,name):
        module = self.module
        #step_length = step_length - clearance
        size_pad = wxSize(touch_width,touch_width)

        size_pad = wxSize(touch_width,touch_width)
        pad = self.smdRectPad(module,size_pad,position,name)
        module.Add(pad)


    def AddRow(self,pos,columns,touch_width,touch_clearance,diogonal_length, name):
        self.AddStartPad(pos,touch_width,touch_clearance,name)

        for n in range(2,columns):
            pos = pos + wxPoint(diogonal_length+touch_clearance,0)
            self.AddMiddlePad(pos,touch_width,touch_clearance,name)

        pos = pos + wxPoint(diogonal_length+touch_clearance,0)
        self.AddFinalPad(pos,touch_width,touch_clearance,name)

    def AddColumn(self,pos,columns,touch_width,touch_clearance,diogonal_length, name):
        self.AddStartPad(pos,touch_width,touch_clearance,name)

        for n in range(2,columns):
            pos = pos + wxPoint(0,diogonal_length+touch_clearance,)
            self.AddMiddlePad(pos,touch_width,touch_clearance,name)

        pos = pos + wxPoint(0,diogonal_length+touch_clearance)
        self.AddFinalPad(pos,touch_width,touch_clearance,name)

    # build the footprint from parameters
    # FIX ME: the X and Y position of the footprint can be better.
    def BuildThisFootprint(self):

        rows              = self.pads["rows"]
        columns           = self.pads["columns"]
        touch_width       = self.pads["diamond_width"]
        touch_clearance   = self.pads["clearance"]
        #touch_length      = (touch_width+touch_clearance)*rows #self.pads["length"]
        

        step_length = (touch_width+touch_clearance) #float(touch_length) / float(rows)

        t_size = self.GetTextSize()
        w_text = self.draw.GetLineThickness()
        ypos = touch_width/2 + t_size/2 + w_text
        self.draw.Value(0, -ypos, t_size)
        ypos += t_size + w_text*2
        self.draw.Reference(0, -ypos, t_size)

        # set SMD attribute
        self.module.SetAttributes(MOD_CMS)

        # starting pad
        #band_width = touch_width

        xpos = -0.5 * (rows - 1) * step_length
        ypos = -0.5 * (columns - 1) * touch_width

        pos = wxPointMM(pcbnew.ToMM(xpos), pcbnew.ToMM(ypos))
        diogonal_length = sqrt(touch_width*touch_width+touch_width*touch_width)

        for b in range(rows):
            self.AddRow(pos,columns,touch_width,touch_clearance,diogonal_length,b)
            pos += wxPoint(0,diogonal_length+touch_clearance)


        pos = wxPointMM(pcbnew.ToMM(xpos), pcbnew.ToMM(ypos))
        pos += wxPoint((diogonal_length+touch_clearance)/2,(diogonal_length+touch_clearance)/2)
        for b in range(columns):
            self.AddColumn(pos,rows,touch_width,touch_clearance,diogonal_length,rows+b)
            pos += wxPoint(diogonal_length+touch_clearance,0)

TouchPadWizard().register()

