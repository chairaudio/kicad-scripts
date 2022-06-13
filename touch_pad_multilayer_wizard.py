# Copyright (C) 2019 CHAIR.AUDIO
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

class TouchPadMultiLayerWizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        """
        Return footprint name.
        This is specific to each footprint class, you need to implement this
        """
        return 'Touch Pad Multi Layer'

    def GetDescription(self):
        """
        Return footprint description.
        This is specific to each footprint class, you need to implement this
        """
        return 'Capacitive Touch Pad with layer-seperated rows and columns wizard'

    def GetValue(self):
        return "TouchPad-MultiLayer-{c}x{r}_{x:g}x{y:g}mm".format(
            r = self.pads['rows'],
            c = self.pads['columns'],
            x = pcbnew.ToMM(self.pads['columns']*(self.pads['diamond_width']+self.pads['clearance'])),
            y = pcbnew.ToMM(self.pads['rows']*(self.pads['diamond_width']+self.pads['clearance']))
            )

    def GenerateParameterList(self):
        self.AddParam("Pads", "columns", self.uInteger, 3, min_value=1)
        self.AddParam("Pads", "rows", self.uInteger, 3, min_value=1)
        self.AddParam("Pads", "diamond_width", self.uMM, 5)
        self.AddParam("Pads", "clearance", self.uMM, 1)
        self.AddParam("Pads", "via_size", self.uMM, 0.5)
        self.AddParam("Pads", "drill_size", self.uMM, 0.2)
        self.AddParam("Pads", "line_thickness", self.uMM, 0.2)
        self.AddParam("Pads", "add_solder_mask", self.uBool, False)

    @property
    def pads(self):
        return self.parameters['Pads']

    # build a rectangular pad
    def smdRectPad(self,module,size,pos,name,mask=False, flip=False):
        pad = PAD(module)
        pad.SetSize(size)
        pad.SetShape(PAD_SHAPE_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        if(mask):
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            fcuSet = LSET(1, F_Cu)
            pad.SetLayerSet(fcuSet)

        if flip:
            pad.Flip( wxPoint(0,0), True )
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName(name)
        pad.SetOrientation(450)
        return pad

    # build a rectangular pad
    def smdLinePad(self,module,size,pos,name,flip,mask=False):
        pad = PAD(module)
        pad.SetSize(size)
        pad.SetShape(PAD_SHAPE_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        if mask:
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            fcuSet = LSET(1, F_Cu)
            pad.SetLayerSet(fcuSet)

        if flip:
            pad.Flip( wxPoint(0,0), True )

        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName(name)
        pad.SetOrientation(0)
        return pad

    def smdTrianglePad(self,module,size,pos,name,up_down=1,left_right=0,rotate=1,mask=False, flip=False):
        pad = PAD(module)
        pad.SetSize(wxSize(size[0],size[1]))
        pad.SetShape(PAD_SHAPE_TRAPEZOID)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        if mask:
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            fcuSet = LSET(1, F_Cu)
            pad.SetLayerSet(fcuSet)

        if flip:
            pad.Flip( wxPoint(0,0), True )
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName(name)
        pad.SetDelta(wxSize(left_right*size[1]*rotate,up_down*size[0]*rotate))
        return pad


    def THRoundPad(self, size, drill,pos,name,mask=False):
        """!
        A round though-hole pad. A shortcut for THPad()
        @param size: pad diameter
        @param drill: drill diameter
        """
        pad = pcbnew.PAD(self.module)
        pad.SetSize(pcbnew.wxSize(size, size))
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        if mask:
            pad.SetLayerSet(pad.PTHMask())
        else:
            tentedViaSet = pad.PTHMask()
            tentedViaSet.removeLayer(F_Mask)
            tentedViaSet.removeLayer(B_Mask)
            pad.SetLayerSet(tentedViaSet)

        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName(name)
        pad.SetDrillSize(pcbnew.wxSize(drill, drill))
        pad.SetOrientation(0)   # rotation is in 0.1 degrees
        return pad


    # This method checks the parameters provided to wizard and set errors
    def CheckParameters(self):
        #TODO - implement custom checks
        pass

    # The start pad is made of a rectangular pad plus a couple of
    # triangular pads facing tips on the middle/right of the first
    # rectangular pad
    def AddStartPadRow(self,position,touch_width,clearance,name,mask):
        module = self.module
        size_pad = wxSize(touch_width,touch_width)
        position=position-wxPoint(touch_width/2,0);
        pad = self.smdTrianglePad(module,size_pad,position,name, 0, 1, 1,mask)
        module.Add(pad)

    # The start pad is made of a rectangular pad plus a couple of
    # triangular pads facing tips on the middle/right of the first
    # rectangular pad
    def AddStartPadColumn(self,position,touch_width,clearance,name,mask):
        module = self.module
        size_pad = wxSize(touch_width,touch_width)
        position=position-wxPoint(0,touch_width/2);
        pad = self.smdTrianglePad(module,size_pad,position,name, 1, 0,-1,mask, True)
        module.Add(pad)


    # compound a "start pad" shape plus a triangle on the left, pointing to
    # the previous touch-pad
    def AddMiddlePad(self,position,touch_width,clearance,name,mask,flip):
        module = self.module
        size_pad = wxSize(touch_width,touch_width)
        pad = self.smdRectPad(module,size_pad,position,name,mask,flip)
        module.Add(pad)

    def AddMiddleVias(self,position,diogonal_length,via_size,drill_size,name):
        module = self.module
        position=position-wxPoint(0,0.75*diogonal_length/2);
        via = self.THRoundPad(via_size,drill_size,position,name)
        module.Add(via)
        position=position+wxPoint(0,0.75*diogonal_length);
        via = self.THRoundPad(via_size,drill_size,position,name)
        module.Add(via)

    def AddStartVia(self,position,diogonal_length,via_size,drill_size,name):
        module = self.module
        position=position+wxPoint(0,0.5*diogonal_length*0.75);
        via = self.THRoundPad(via_size,drill_size,position,name)
        module.Add(via)

    def AddFinalVia(self,position,diogonal_length,via_size,drill_size,name):
        module = self.module
        position=position-wxPoint(0,0.75*diogonal_length/2);
        via = self.THRoundPad(via_size,drill_size,position,name)
        module.Add(via)


    def AddFinalPadRow(self,position,touch_width,clearance,name,mask):
        module = self.module
        size_pad = wxSize(touch_width,touch_width)
        position=position-wxPoint(touch_width/2,0);
        pad = self.smdTrianglePad(module,size_pad,position,name, 0, 1,-1,mask)
        module.Add(pad)

    def AddFinalPadColumn(self,position,touch_width,clearance,name,mask):
        module = self.module
        size_pad = wxSize(touch_width,touch_width)
        position=position-wxPoint(0,touch_width/2);
        pad = self.smdTrianglePad(module,size_pad,position,name, 1, 0, 1,mask,True)
        module.Add(pad)


    def AddRow(self,pos,row,touch_width,touch_clearance,diogonal_length, name,mask):
        self.AddStartPadRow(pos,diogonal_length/2,touch_clearance,name,mask)
        pos = pos + wxPoint(diogonal_length/2+touch_clearance,0)

        for n in range(1,row):
            self.AddMiddlePad(pos,touch_width,touch_clearance,name,mask,False)
            pos = pos + wxPoint(diogonal_length+touch_clearance,0)

        self.AddFinalPadRow(pos,diogonal_length/2,touch_clearance,name,mask)

    def AddColumn(self,pos,columns,touch_width,touch_clearance,diogonal_length, name, via_size,drill_size,line_thickness,mask):
        self.AddStartPadColumn(pos,diogonal_length/2,touch_clearance,name,mask)
        #self.AddStartVia(pos - wxPoint(0,diogonal_length/2),diogonal_length,via_size,drill_size,name)

        linepos = pos + wxPoint(0,0.5*touch_clearance)
        linelength = touch_clearance + 0.25 * diogonal_length
        size_line = wxSize(line_thickness,linelength)
        module = self.module
        pad = self.smdLinePad(module,size_line,linepos,name,1,False)
        module.Add(pad)

        pos = pos + wxPoint(0,diogonal_length/2+touch_clearance)


        for n in range(1,columns):
            self.AddMiddlePad(pos,touch_width,touch_clearance,name,mask,True)
            #self.AddMiddleVias(pos,diogonal_length,via_size,drill_size,name)
            linepos = pos + wxPoint(0,diogonal_length*0.5+0.5*touch_clearance)
            pad = self.smdLinePad(module,size_line,linepos,name,1,False)
            module.Add(pad)
            pos = pos + wxPoint(0,diogonal_length+touch_clearance)

        self.AddFinalPadColumn(pos,diogonal_length/2,touch_clearance,name,mask)
        #self.AddFinalVia(pos,diogonal_length,via_size,drill_size,name)


    # build the footprint from parameters
    def BuildThisFootprint(self):

        rows              = self.pads["rows"]
        columns           = self.pads["columns"]
        diogonal_length   = self.pads["diamond_width"]
        touch_clearance   = self.pads["clearance"]
        via_size		  = self.pads["via_size"]
        drill_size		  = self.pads["drill_size"]
        line_thickness	  = self.pads["line_thickness"]
        touch_width       = sqrt(diogonal_length*diogonal_length/2)
        mask              = self.pads["add_solder_mask"]


        t_size = self.GetTextSize()
        w_text = self.draw.GetLineThickness()
        ypos = (diogonal_length+touch_clearance)*float(rows*0.5+0.5) + t_size*0.5 + w_text
        self.draw.Value(0, -ypos, t_size)
        ypos += t_size + w_text*2
        self.draw.Reference(0, -ypos, t_size)

        # set SMD attribute
        self.module.SetAttributes(PAD_ATTRIB_SMD)


        # starting pad
        xpos = diogonal_length/2- 0.5 * columns * (diogonal_length+touch_clearance)
        ypos = diogonal_length/2+touch_clearance/2 - 0.5 * rows * (diogonal_length+touch_clearance)

        pos = wxPointMM(pcbnew.ToMM(xpos), pcbnew.ToMM(ypos))
        module = self.module

        width= (self.pads['columns']*(self.pads['diamond_width']+self.pads['clearance']))*0.99
        size_pad = wxSize(width,line_thickness)


        for b in range(rows):
        	self.AddRow(pos,columns,touch_width,touch_clearance,diogonal_length,"r{r}".format(r=b),mask)
        	line_pos = wxPoint(pos[0]+width*0.5-diogonal_length/2,pos[1])
        	pad = self.smdLinePad(module,size_pad,line_pos,"r{r}".format(r=b),0,mask)
        	module.Add(pad)
        	pos += wxPoint(0,diogonal_length+touch_clearance)


        pos = wxPointMM(pcbnew.ToMM(xpos), pcbnew.ToMM(ypos))
        pos += wxPoint(touch_clearance/2,-touch_clearance/2)
        for b in range(columns):
            self.AddColumn(pos,rows,touch_width,touch_clearance,diogonal_length,"c{c}".format(c=b),via_size,drill_size,line_thickness,mask)
            pos += wxPoint(diogonal_length+touch_clearance,0)





TouchPadMultiLayerWizard().register()

