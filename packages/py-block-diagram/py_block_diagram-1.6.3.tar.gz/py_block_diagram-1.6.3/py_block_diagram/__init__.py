"""
This module exists to model feedback control systems using block
diagrams.  A feedback control system is modeled using the
`block_diagram` class.  The individual components of the system are
modeled using sensors, actuators, and blocks.  The root block class is
`block`.  There are also helper root classes that are kind of like
abstract classes for things that generate Arduino code and things that
generate Python code: `arduino_code_gen_object` and
`python_code_gen_obejct`.

## Wire Routing and Waypoints

If wires end up on top of one another, it makes the block diagram
harder to understand and troubleshoot.  Because the block diagram is
shown on a matplotlib canvas, we cannot simply drag and drop the wires
to clarify things.

A wire is associated with the block whose input it is - the block
where the wire ends.  The start point and end point of the wire are
known, but intermediate points are not.  So, simply clicking on the
wire will not allow us to select the corresponding wire.

So, how should wire waypoints be specified when needed?

- how do I identify the wire we are talking about?
    - find the block where the wire ends
    - decided if we are talking about wire 1 or wire 2 if
      the block has two inputs
- how do I specify where the waypoint is located?
    - abs coordinates seem risky
    - specify relative to the start or end of the wire using
      relative x and/or y offsets
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from numpy import array
from py_block_diagram import digcomp
import copy, os, sys
import re
from krauss_misc import txt_mixin
version = "1.6.3"
# lists of things for saving blocks to csv
abs_labels = ['abs_x','abs_y']
relative_attrs = ['rel_block_name','rel_pos','rel_distance','xshift','yshift']
csv_params_batch1 = ['variable_name','label','arduino_class',\
                     'input_block1_name','input_block2_name',\
                     'width','height']
#[block_type] + batch1_list + pos_list
#[placement_type] + abs_list + relative_list
csv_labels = ['block_type'] + csv_params_batch1 + ['placement_type'] + abs_labels + relative_attrs

max_csv_params = 10
params_labels = ['param%i' % i for i in range(1,max_csv_params+1)]
csv_labels += params_labels


def parse_array_str(str_in):
    out = str_in.strip()
    # get rid of space or tab between opening square bracket
    # and first element:
    p = re.compile(r"\[\s*")
    out = p.sub("[", out)
    # and then do the space or tabs before closing bracket:
    p2 = re.compile(r"\s*\]")
    out = p2.sub("]", out)
    # now any remaining space or tab combinations are just commas:
    p3 = re.compile(r'\s+')
    out = p3.sub(",", out)
    # deal with repeated commas (not sure where they came from)
    p4 = re.compile(",+")
    out = p4.sub(",", out)
    myarray = eval(out)
    return myarray



def value_from_str(string_in):
    try:
        out = float(string_in)
        out2 = int(out)
        if abs(out2-out) < 1e-5:
            # it is basically an integer
            return out2
        else:
            return out
    except:
        # cannot be converted to float
        return string_in


def clean_chunk(chunk_in):
    chunk_out = [item for item in chunk_in if item]
    return chunk_out


def fix_one_delimiter(mylist, delim='[',close_delim=']'):
    outlist = []
    i = 0
    N = len(mylist)
    while (i < N):
        item = mylist[i]
        if delim in item and close_delim not in item:
            # keeping adding the next item until the match
            # happens
            while close_delim not in item:
                i += 1
                item += ',' + mylist[i]
        outlist.append(item)
        i += 1
    return outlist



def break_string_pairs_to_dict(mylist):
    kwargs = {}
    print("mylist:")
    print(mylist)
    for item in mylist:
        print("item: %s" % item)
        key, val_str = item.split(":",1)
        value = value_from_str(val_str)
        kwargs[key] = value

    return kwargs


def get_wire_color(plot_args):
    """Not doing a good job handling passing line color, color,
    or wire_color to various drawing and plotting functions.  Also,
    ax.plot uses color while ax.arrow uses fc or facecolor.  I need
    to get the color and then not pass offending keys into **kwargs
    further down"""
    mykeys = ['fc','color','wire_color']#<-- reverse order of preference
    color='k'
    for key in mykeys:
        if key in plot_args:
            color=plot_args.pop(key)
    return color, plot_args


def hard_code_cal(rpifile):
    print('in hard_code_cal')
    mylist = rpifile.list
    # problem: there are multiple places where check_cal is called
    # solution: hard code them all (none of them matter)
    myinds = mylist.findall("check_cal();")
    for myind in myinds:
        print("myind = %s" % myind)
        myline = mylist[myind]
        mysplitlist = myline.split('calibrated')
        ws = mysplitlist[0]
        newline = ws + "calibrated = 1;"
        print("newline: %s" % newline)
        mylist[myind] = newline
    return mylist


def csv_row_to_dict(row, labels):
    # Approach:
    # - make a dict from row and labels
    # - try converting each value to a float or int
    #   using the value_from_str function
    # - handle the param%i key:value pairs
    #     - use the pop method and build a list of the "key:value" pairs
    #       to pass to break_string_pairs_to_dict
    row_values = [value_from_str(item) for item in row]
    mydict = dict(zip(labels, row_values))
    #print("mydict: %s" % mydict)
    key_value_strs = []
    for i in range(20):
        key = "param%i" % i
        if key in mydict:
            curstr = mydict.pop(key).strip()
            if curstr:
                key_value_strs.append(curstr)
    #print("key_value_strs: %s" % key_value_strs)
    key_value_kwargs = break_string_pairs_to_dict(key_value_strs)

    mydict.update(key_value_kwargs)
    return mydict


def process_actuator_or_sensor_chunk(chunk):
    mydict = {}
    my_name_list = []

    for line in chunk:
        curlist = line.split(',')
        clean_list = list(filter(None, curlist))

        class_name = clean_list.pop(0)
        variable_name = clean_list.pop(0)
        kwargs = break_string_pairs_to_dict(clean_list)
        myclass = actuator_and_sensor_class_dict[class_name]
        mything = myclass(variable_name=variable_name, **kwargs)
        mydict[variable_name] = mything
        my_name_list.append(variable_name)


    return mydict, my_name_list


def find_midpoint(start_point, end_point, wire_style='vh'):
    if wire_style == 'vh':
        # midpoint is above or below start and left or right of end
        # - x is the same as the start and y is the same as the end
        midpoint = (start_point[0],end_point[1])
    elif wire_style == 'hv':
        # the opposite case as 'vh':
        midpoint = (end_point[0],start_point[1])
    return midpoint



def find_end_point(start_block, end_block, approach='h'):
    """The (x,y) coordinates are to the center of each block.  A wire
    needs to start or end at the left, right, bottom, or top of the
    block.  Which side it is depends on the x and y coordinates of
    start_block and end_block and whether the approach is horizontal
    or vertical ('h' or 'v').

    I am pretty sure that finding the start point only requires
    reversing the start_block and end_block."""
    if approach == 'h':
        # going horizontal
        if end_block.x > start_block.x:
            # end_block is right of start_block, find left edge of end_block
            myx = end_block.x - end_block.width*0.5
        else:
            # end_block is left of start_block, find right edge of end_block
            myx = end_block.x + end_block.width*0.5
        mypoint = (myx, end_block.y)
    elif approach == 'v':
        # going vertical
        if end_block.y > start_block.y:
            # end_block is above start_block
            myy = end_block.y - end_block.height*0.5
        else:
            # end_block is below start_block
            myy = end_block.y + end_block.height*0.5
        mypoint = (end_block.x, myy)

    return mypoint



def find_start_point(start_block, end_block, approach='h'):
    return find_end_point(end_block, start_block, approach=approach)



def get_wire_style(start_point, end_point, L_style='vh', tol=0.1):
    wire_delta_x = end_point[0] - start_point[0]
    wire_delta_y = end_point[1] - start_point[1]

    if np.abs(wire_delta_y) < tol:
        wire_style = 'h'
    elif np.abs(wire_delta_x) < tol:
        wire_style = 'v'
    else:
        wire_style = L_style

    return wire_style



def draw_segment_se(ax, start_point, end_point, \
        linestyle='-', **plot_args):
    """Draw a line segment on axis ax from start_point to end_point.

    start_point and end_point are (x,y) pairs."""
    color, plot_args = get_wire_color(plot_args)
    print("in draw_segment_se, color = %s" % color)
    start_x = start_point[0]
    start_y = start_point[1]
    end_x = end_point[0]
    end_y = end_point[1]
    print("myx: %s" % [start_x, end_x])
    print("myy: %s" % [start_y, end_y])
    print("color: %s" % color)
    ax.plot([start_x, end_x], [start_y, end_y], color=color,
            linestyle=linestyle, **plot_args)


def _draw_arrow(ax, start_x, start_y, dx, dy, \
                lw=1, ec=None, **plot_args):
    """wrapper for matplotlib ax.arrow method - draw an arrow that
    starts at (start_x, start_y) and ends at a point shifted by
    (dx,dy)."""
    width = 0.01
    head_width = 15*width
    head_length = 2*head_width
    color, plot_args = get_wire_color(plot_args)

    print(' in _draw_arrow, color = %s' % color)

    ax.arrow(start_x, start_y, dx, dy, \
             lw=lw, fc=color, ec=color, \
             width=0.01, \
             head_width=head_width, head_length=head_length, \
             #overhang = self.ohg, \
             length_includes_head=True, clip_on = False, \
             **plot_args)


def draw_arrow_se(ax, start_point, end_point, **kwargs):
    """Draw an arrow on axis ax from start_point to end_point.

    start_point and end_point are (x,y) pairs."""
    start_x = start_point[0]
    start_y = start_point[1]
    end_x = end_point[0]
    end_y = end_point[1]
    dx = end_x - start_x
    dy = end_y - start_y
    _draw_arrow(ax, start_x, start_y, dx, dy, **kwargs)


def draw_line_segment_possible_L_optional_array(ax, \
                                                start_point, \
                                                end_point, \
                                                L_style='vh', arrow=False,**plot_args):
    wire_style = get_wire_style(start_point, end_point, L_style)

    if arrow:
        func2 = draw_arrow_se
    else:
        func2 = draw_segment_se

    if len(wire_style) == 1:
        # purely vertical or horizontal
        func2(ax, start_point, end_point, **plot_args)
    else:
        # - so far, we have two options: 'vh' or 'hv'
        # - approach:
        #     - plot line from start to midpoint
        #     - draw arrow from midpoint to end
        if wire_style == 'vh':
            # midpoint is above or below start and left or right of end
            # - x is the same as the start and y is the same as the end
            midpoint = (start_point[0],end_point[1])
        elif wire_style == 'hv':
            # the opposite case as 'vh':
            midpoint = (end_point[0],start_point[1])

        print("start_point: %s, midpoint: %s, end_point: %s" % \
                (start_point, midpoint, end_point))
        print('func2: %s' % func2)
        draw_segment_se(ax, start_point, midpoint, **plot_args)
        func2(ax, midpoint, end_point, **plot_args)



def draw_wire(ax, start_point, end_point, waypoints=[], L_style='vh', **plot_args):
    """Draw a wire from start_point to end_point passing through
    waypoints (if given).  Waypoints are in order from the start of
    the wire to the end.

    If only start and end are given and they are offset in x and y, an
    L shape is needed.  Do I assume 'vh' or 'hv'?  It feels like a
    vertical ending only makes sense for summing junctions."""

    # - make a list of [start_point, waypoints, end_point]
    # - draw line segments between points until the last one
    # - draw an arrow from the second to last point to the last one
    full_list = [start_point] + waypoints + [end_point]
    print("full_list: %s" % full_list)

    prev_point = full_list[0]

    for point in full_list[1:-1]:
        # skip the first point and stop before the last point
        print("point: %s, prev_point: %s" % (point, prev_point))
        draw_line_segment_possible_L_optional_array(ax, prev_point, point, L_style=L_style, \
                                                    arrow=False, **plot_args)
        prev_point = point

    draw_line_segment_possible_L_optional_array(ax, full_list[-2], \
                                                full_list[-1], \
                                                L_style=L_style, \
                                                arrow=True, **plot_args)



def param_str_from_list_of_tuples(tup_list):
    """Given a list of tuples: [(str1, val1), (str2, val2), ...],
    generate a string that could be used in initialization code:
    'str1=val1, str2=val2,...'"""
    out_str = ""
    for val, attr in tup_list:
        if out_str:
            out_str +=", "
        next_str = "%s=%s" % (val, attr)
        out_str += next_str
    return out_str


def process_menu_params_line(linein):
    mystr, int_str = linein.split(",")
    mystr = mystr.strip()
    myint = int(int_str.strip())
    return mystr, myint


class arduino_code_gen_object(object):
    """A mix-in class for any object that generates Arduino code.  The
    main purpose of this class is to ensure consistancy in derived
    classes of objects that will need to generate Arduino code.

    All blocks in a control system block diagram should probably
    derive from this class.  Sensors and actuators are two examples of
    classes that should be able to generate Arduino code but that are
    technically not blocks.  Hence, this code is not going directly in the
    block class."""
    def __init__(self, variable_name='myname', arduino_class='myclass', \
                 param_list=[], default_params={}):
        self.variable_name = variable_name
        self.arduino_class = arduino_class
        self.param_list = param_list
        self.default_params = default_params


    def _get_arduino_param_str(self):
        # must set the variable self._arduino_param_str
        print("problem with %s" % self.variable_name)
        raise NotImplementedError


    def get_arduino_init_code(self):
        """Code to be executed to create an instance of the block in
        Arduino code"""
        # specific example:
        #
        # step_input u = step_input(0.5, 150);
        #
        # assumed pattern:
        #
        # arduino_class variable_name = arduino_class(param_str)
        self._get_arduino_param_str()
        pat = '%s %s = %s(%s);'
        line1 = pat % (self.arduino_class, \
                       self.variable_name, \
                       self.arduino_class, \
                       self._arduino_param_str)
        return [line1]


    def get_arduino_setup_code(self):
        # probably not common, so let it be ok not to override:
        return []


    def get_arduino_menu_code(self):
        # probably not common, so let it be ok not to override:
        return []


    def get_arduino_menu2_code(self):
        return []


    def get_arduino_menu3_code(self):
        return []


    def get_arduino_loop_code(self):
        """Code to be executed in the Arduino loop method for the block"""
        raise NotImplementedError


    def get_arduino_secondary_loop_code(self):
        """Probably not needed for most blocks, but required for
        some plants that need to send commands at the end of the loop"""
        return []


    def get_arduino_print_code(self):
        # Assuming int output for now
        # - print_comma_then_int(G.read_output());
        print_line = "print_comma_then_int(%s.read_output());" % self.variable_name
        return [print_line]


    def get_csv_label(self):
        """Just creating a helper function to make it easy to change this
        behavior in the future if I need to.

        This method returns the label that will go at the top of the column of
        the csv data file.  True csv logging is probably an rpi thing, but this
        could also be used in serial printing of well formatted csv data."""
        return self.variable_name


class rpi_code_gen_object(arduino_code_gen_object):
    """I want to support both arduino and raspberry pi (mostly via wiringPi)
    codegen.  I will probably use pure arduino during the first few weeks of
    345 lab.  Other people will want to use pure Arduino.  But I will need the
    Raspberry Pi version for the cart/pendulum systems.

    There are a few nuances that make RPi code different from Arduino, but
    I don't know what they all are yet.  We will default to Arduino methods for
    now for most things RPi.

    In most cases, rpi code will default to Arduino code unless there is some
    reason not to.  I think that means rpi_code_gen_object should inherit from
    arduino_code_gen_object, but that means all other objects have to switch to
    being derived from rpi_code_gen_object and nothing can ever inherit from
    both."""
    def get_rpi_loop_code(self):
        # default to arduino loop code unless overwritten
        mylist = self.get_arduino_loop_code()
        return mylist


    def get_rpi_secondary_loop_code(self):
        """For the cart pendulum plant, the loop variable is different between
        Arduino and RPi.  Most blocks will not need to do anything here, so
        default is to return an empty list."""
        return []


    def get_rpi_print_string(self):
        """RPi printing probably means logging to csv with fprintf or otherwise
        using printf.  So, each print block will return a string that gets the
        output and then those strings will get combined in some way in a call
        to fprintf or printf"""
        mystr = "%s.read_output()" % self.variable_name
        return mystr


    def get_rpi_end_test_code(self):
        """Code that exectutes when a test is finished, such as setting
        actuators to zero"""
        return []


    def get_rpi_start_test_code(self):
        """Code that exectutes when a test is finished, such as setting
        actuators to zero"""
        return []


class arduino_code_gen_no_params(arduino_code_gen_object):
    """Class for an object that generates Arduino code whose input
    parameters are empty, such as a loop counter or time block"""
    def _get_arduino_param_str(self):
        # h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin */
        self._arduino_param_str = ""
        return ""


class arduino_code_gen_loop_no_inputs(arduino_code_gen_object):
    """Initially, I made all Arduino blocks take time as a float as
    the only input to their find_output function in the loop.  But I
    now think this is potentially confusing to users, because most
    blocks don't depent on time and some blocks will just be
    constants.  So, I am creating this class for blocks whose
    find_output method takes no input variables.

    Note: most blocks still have one or more input blocks, but those
    are set as pointers in the setup (Arduino) or secondary init
    (Python) code.  So, most blocks will read the outputs from their
    input blocks inside the find_output method, but there are no
    separate input paremeters."""
    def get_arduino_loop_code(self):
        """Code to be executed in the Arduino loop method for the block"""
        # assumed form:
        # u.find_output();
        pat = '%s.find_output();'
        line1 = pat % self.variable_name
        return [line1]



class python_code_gen_obejct(object):
    def __init__(self, variable_name="py_gen_obj", py_params=[]):
        #print("in python_code_gen_obejct __init__")
        self.variable_name = variable_name
        self.py_params = py_params


    def _lookup_params_build_string(self, param_list):
        outstr = ""
        for attr in param_list:
            if outstr:
                # append a comma if this isn't the first pass through
                # the loop
                outstr += ', '
            val = getattr(self, attr)
            if type(val) == str:
                new_str = '%s="%s"' % (attr, val)
            else:
                new_str = '%s=%s' % (attr, val)
            outstr+= new_str
        return outstr


    def _get_python_param_str(self):
        msg = """python codegen object must have a parameter py_params that is a list of strings
        that refer to attributes specified when initiating an instance of the class."""
        assert hasattr(self,'py_params'), msg
        py_params = getattr(self, "py_params")
        #assert len(py_params) > 0, msg#<-- a summing junction will have empty params

        outstr = self._lookup_params_build_string(py_params)
        self._py_params = outstr
        return outstr


    def get_python_init_code(self, indent=''):
        myparamstr = self._get_python_param_str()
        #mod_str = type(self).__module__
        mod_str = "pybd"
        class_name_str = type(self).__name__
        self.python_class_str = "%s.%s" % (mod_str, class_name_str)
        pat = '%s = %s(%s)'
        line1 = pat % (self.variable_name, \
                       self.python_class_str, \
                       myparamstr)
        return [line1]



    def get_python_secondary_init_code(self):
        """After creating all blocks, the inputs will need to be set.
        It will not always be possible to create the blocks in an
        order where all input blocks exists before a block is created.
        So, this code block is for setup code after all block
        instances have been created.

        For source blocks that have no inputs, no code is necessary so
        an empty list is returned."""
        return []


    def get_python_loop_code(self, istr="i"):
        """Get the code that will be called inside the main loop in
        the python experimental file.  For many blocks, this will just be
        myname.find_output(i)

        Keep in mind that this means that all blocks need to have a
        find_output method.

        It might make sense to move this to the block class at a later
        time.  A sensor or actuator might have their loop code called
        the plant object."""
        line1 = "%s.find_output(%s)" % (self.variable_name, istr)
        return [line1]


    def get_python_secondary_loop_code(self, **kwargs):
        """If a block needs to do something at the end of the loop,
        its code would be generated using this method.  For example,
        an i2c plant might need to read its sensors at the start of
        the loop and then send its commands at the end of the loop.
        Reading the sensors needs to happen before commands are sent
        to the actuators."""
        return []


class no_code_python_block(python_code_gen_obejct):
    """Base class for blocks that do not have any Python code
    associated with them, such as an Arduino plant or an output node.

    This class has all the same get code methods as
    python_code_gen_obejct, but they all return empty lists."""
    def get_python_init_code(self):
        return []


    def get_python_secondary_init_code(self):
        return []


    def get_python_loop_code(self):
        return []


class sensor(rpi_code_gen_object, python_code_gen_obejct):
    def get_csv_list_for_row(self):
        return get_csv_for_actuator_or_sensor(self)

    def isplaced(self):
        """Determine whether or not a sensor has beeen placed."""
        if not hasattr(self, 'x'):
            return False
        elif self.x is None:
            return False
        elif self.x is not None:
            return True

class i2c_sensor(sensor):
    def __init__(self, NUM_BYTES=6, py_params=[], \
                 variable_name='i2c_sens', arduino_class='i2c_sensor', \
                 param_list=['NUM_BYTES'], \
                 default_params={'NUM_BYTES':6}, \
                 ):
        python_code_gen_obejct.__init__(self, variable_name=variable_name, py_params=py_params)
        self.NUM_BYTES = NUM_BYTES
        self.arduino_class = arduino_class


    def _get_arduino_param_str(self):
        # h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin */
        params = "%i" % (self.NUM_BYTES)
        self._arduino_param_str = params
        return self._arduino_param_str






class encoder(sensor):
    def __init__(self, pinA=2, pinB=11, \
                 interrupt_number=0, \
                 sensitivity=1, \
                 variable_name='encoder_sensor', arduino_class='encoder', \
                 param_list=['pinA','pinB','interrupt_number','sensitivity'], \
                 default_params={'pinA':2,'pinB':11, 'interrupt_number':0, \
                       'sensitivity':1}):
        sensor.__init__(self, variable_name=variable_name, \
                        arduino_class=arduino_class, param_list=param_list, \
                        default_params=default_params)
        self.pinA = pinA
        self.pinB = pinB
        self.interrupt_number = interrupt_number#Arduino interrupt
                                                #number to attach to
                                                #the encoder (depends on pin A)
        self.sensitivity = sensitivity


    def _sensitivity_class_asjust(self):
        if self.sensitivity == 4:
            self.arduino_class = "encoder_quad_sense"


    def init_code_sensitivity_one(self):
        line1 = '%s %s = %s(%i);' % (self.arduino_class, \
                                    self.variable_name, \
                                    self.arduino_class, \
                                    self.pinB)

        outlist = [line1]
        outlist.append('')
        line2 = "void %s_isr_wrapper() {" % self.variable_name
        line3 = "    %s.encoderISR();" % self.variable_name
        line4 = "}"
        outlist.extend([line2, line3, line4,''])
        return outlist



    def init_code_sensitivity_four(self):
        line1 = '%s %s = %s(encoderPinA, encoderPinB);' % (self.arduino_class, \
                                    self.variable_name, \
                                    self.arduino_class, \
                                    )

        outlist = [line1]
        outlist.append('')
        #void encoder_sensor_isr_A_wrapper() {
        #//Serial.println("A");
        #encoder_sensor.encoderISRA();
        #}

        line2 = "void %s_isr_A_wrapper() {" % self.variable_name
        line3 = "    %s.encoderISRA();" % self.variable_name
        line4 = "}"
        line5 = "void %s_isr_B_wrapper() {" % self.variable_name
        line6 = "    %s.encoderISRB();" % self.variable_name
        line7 = "}"

        outlist.extend([line2, line3, line4,'',line5, line6, line7,""])
        return outlist



    def get_arduino_init_code(self):
        # encoder enc = encoder(11);
        self._sensitivity_class_asjust()
        if self.sensitivity == 1:
            code = self.init_code_sensitivity_one()
        elif self.sensitivity == 4:
            code = self.init_code_sensitivity_four()
        return code


    def get_arduino_setup_code(self):
        self._sensitivity_class_asjust()
        if self.sensitivity == 1:
            code = self.get_arduino_setup_code_sensitivity_one()
        elif self.sensitivity == 4:
            code = self.get_arduino_setup_code_sensitivity_four()
        return code




    def get_arduino_setup_code_sensitivity_one(self):
        #attachInterrupt(0, enc_isr_wrapper, RISING);
        line1 = "attachInterrupt(%i, %s_isr_wrapper, RISING);" % (self.interrupt_number, \
                                                                  self.variable_name)
        return [line1]


    def get_arduino_setup_code_sensitivity_four(self):
        #attachInterrupt(0, enc_isr_wrapper, RISING);
        line1 = "attachInterrupt(digitalPinToInterrupt(encoderPinA), %s_isr_A_wrapper, CHANGE);" % \
                self.variable_name
        line2 = "attachInterrupt(digitalPinToInterrupt(encoderPinB), %s_isr_B_wrapper, CHANGE);" % \
                self.variable_name
        line3 = "pinMode(encoderPinA, INPUT_PULLUP);"
        line4 = "pinMode(encoderPinB, INPUT_PULLUP);"
        return [line1, line2, line3, line4]


    def get_arduino_loop_code(self):
        # assume the plant handles this and the encoder doesn't need
        # to do anything explicitly in the loop
        return []


    def get_arduino_menu2_code(self):
        #   enc.encoder_count = 0;
        line1 = "%s.encoder_count = 0;" % self.variable_name
        return [line1]


    def get_arduino_menu3_code(self):
        line1 = 'Serial.print("encoder reading: ");'
        line2 = 'Serial.println(%s.encoder_count);' % self.variable_name
        return [line1, line2]



class analog_input(sensor):
    def __init__(self, ai_pin="A0", \
                 variable_name='ai_sensor', arduino_class='analog_sensor', \
                 param_list=['ai_pin'], \
                 default_params={'ai_pin':'A0'}):
        sensor.__init__(self, variable_name=variable_name, \
                        arduino_class=arduino_class, param_list=param_list, \
                        default_params=default_params)
        self.ai_pin = ai_pin


    def _get_arduino_param_str(self):
        # h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin */
        params = "%s" % self.ai_pin
        self._arduino_param_str = params
        return self._arduino_param_str


class custom_sensor(sensor):
    """A class for sensors such as the accel z channel of an MPU6050
    where the sensor class if written by the user or included in the
    .ino file via a template or something.  This is done so that the
    Arduino rtblockdiagram method does not depend on libraries like
    MPU6050.  I don't want potential users of my rtblockdiagram
    library to have to install many sensor libraries before being able
    to use my code."""
    def __init__(self, variable_name='myname', arduino_class='myclass', init_params='', \
                 param_list=['arduino_class','init_params'], \
                 default_params={'arduino_class':'myclass', 'init_params':''}):
        """The Arduino code to create an instance of the sensor will be:

        myclass myname = myclass(init_params);"""
        sensor.__init__(self, variable_name=variable_name, \
                        arduino_class=arduino_class, param_list=param_list, \
                        default_params=default_params)
        self.init_params = init_params
        self._arduino_param_str = init_params
        print("in custom sensor init, self.init_params = %s" % self.init_params)

    def _get_arduino_param_str(self):
        # must set the variable self._arduino_param_str
        print("in _get_arduino_param_str, paramstr = %s" % \
                self._arduino_param_str)
        return self._arduino_param_str


class accelerometer(custom_sensor):
    #accel = pybd.custom_sensor("myaccel", "azaccel6050", "&accelgyro")
    def __init__(self, variable_name='myaccel', arduino_class='azaccel6050', \
                 init_params='&accelgyro', \
                 param_list=['arduino_class','init_params'], \
                 default_params={'arduino_class':'azaccel6050', \
                                 'init_params':'&accelgyro'}):
        """MPU 6050 accel gyro with only z axis used in one of my Arduino
        templates.  The azaccel6050 class is defined in that template.
        """
        print("in accel init, init_params = %s" % init_params)
        custom_sensor.__init__(self, variable_name=variable_name, \
                        arduino_class=arduino_class, \
                        init_params=init_params, \
                        param_list=param_list, \
                        default_params=default_params)



def get_param_key_value_csv_list(thing):
    mylist = []
    pat = "%s:%s"

    if not hasattr(thing, "param_list"):
        # do nothing
        print("no param_list")
        return mylist

    key_list = thing.param_list
    #print("key_list: %s" % key_list)
    common_params = ["loop_number"]
    for key in common_params:
        if key not in key_list:
            if hasattr(thing, key):
                key_list.append(key)


    for key in key_list:
        value = getattr(thing, key)
        # it doesn't do any good to store a reference to a block, sensor, or actuator
        # - always look up thier variable names
        # - approach:
        #   - if value has a "variable_name" parameter, use that instead
        #
        ## lookup_classes = [block, actuator, sensor]
        ## for curclass in lookup_classes:
        ##     if isinstance(value, curclass):
        ##         value = value.variable_name
        ##         break
        if hasattr(value, "variable_name"):
            value = value.variable_name
        if value is not None:
            #only save values that are not None
            cur_str = pat % (key, value)
            mylist.append(cur_str)

    return mylist


def get_csv_for_actuator_or_sensor(thing):
    """Convert the actuator or sensor instance into a list that is
    ready to be converted to csv.

    format:
    actuator_type, variable_name, key1:val1, key2:val2, ...

    The key:value pairs will come from thing.param_list"""
    actuator_type = type(thing).__name__
    variable_name = thing.variable_name
    mylist = [actuator_type, variable_name]

    second_list = get_param_key_value_csv_list(thing)
    mylist.extend(second_list)

    return mylist



class actuator(rpi_code_gen_object):
    def get_csv_list_for_row(self):
        return get_csv_for_actuator_or_sensor(self)


## actuator_list = ['h_bridge', 'custom_actuator', 'pwm_output']#from running findallsubclasses in jupyter
## actuator_params_dict = {'h_bridge':['in1_pin', 'in2_pin', 'pwm_pin'], \
##                         'pwm_output':['pwm_pin'], \
##                         'custom_actuator':['arduino_class', 'init_params'], \
##                         }
## h_bridge_defaults = {'in1_pin':6, \
##                      'in2_pin':4, \
##                      'pwm_pin':9}


class h_bridge(actuator):
    def __init__(self,  in1_pin=6, \
                 in2_pin=4, \
                 pwm_pin=9, \
                 variable_name='HB_actuator', arduino_class='h_bridge_actuator', \
                 param_list=['in1_pin', 'in2_pin', 'pwm_pin'], \
                 default_params={'in1_pin':6, 'in2_pin':4, 'pwm_pin':9},
                 ):
        actuator.__init__(self, variable_name=variable_name, \
                          arduino_class=arduino_class, param_list=param_list, \
                          default_params=default_params)
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.pwm_pin = pwm_pin


    def _get_arduino_param_str(self):
        # h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin */
        params = "%i, %i, %i" % (self.in1_pin, self.in2_pin, self.pwm_pin)
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_arduino_loop_code(self):
        # assume the plant handles this and the encoder doesn't need
        # to do anything explicitly in the loop
        return []


    def get_arduino_setup_code(self):
        # HB.setup();
        setup_line = "%s.setup();" % self.variable_name
        return [setup_line]


class i2c_actuator(actuator):
    """Assume that i2c_plant handles most of the code (setup, loop, ...)"""
    def __init__(self,  NUM_BYTES=5, \
                 variable_name='i2c_act', arduino_class='i2c_actuator', \
                 param_list=['NUM_BYTES'], \
                 default_params={'NUM_BYTES':5},
                 ):
        actuator.__init__(self, variable_name=variable_name, \
                          arduino_class=arduino_class, param_list=param_list, \
                          default_params=default_params)
        self.NUM_BYTES = NUM_BYTES


    def _get_arduino_param_str(self):
        # h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin */
        params = "%i" % (self.NUM_BYTES)
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_arduino_loop_code(self):
        # assume the plant handles this and the encoder doesn't need
        # to do anything explicitly in the loop
        return []


    def get_arduino_setup_code(self):
        return []



class custom_actuator(actuator):
    """A class for actuators like the DualMax motor driver used on my
    pendulum/cart systems.  I don't want users of this library to be
    required to install all Pololu drivers.
    """
    def __init__(self, variable_name='myact', arduino_class='myclass', init_params='', \
                 param_list=['arduino_class','init_params'],\
                 default_params={'arduino_class':'myclass','init_params':''}):
        """The Arduino code to create an instance of the sensor will be:

        myclass myname = myclass(init_params);"""
        actuator.__init__(self, variable_name=variable_name, \
                          arduino_class=arduino_class, param_list=param_list, \
                          default_params=default_params)
        self.init_params = init_params
        self._arduino_param_str = init_params


    def _get_arduino_param_str(self):
        # must set the variable self._arduino_param_str
        return self._arduino_param_str


class pwm_output(h_bridge):
    def __init__(self, pwm_pin=6, \
                 variable_name='pwm_out', arduino_class='pwm_output', \
                 param_list=['pwm_pin'],\
                 default_params={'pwm_pin':6}):
        sensor.__init__(self, variable_name=variable_name, \
                        arduino_class=arduino_class, param_list=param_list, \
                        default_params=default_params)
        self.pwm_pin = pwm_pin


    def _get_arduino_param_str(self):
        params = "%i" % self.pwm_pin
        self._arduino_param_str = params
        return self._arduino_param_str


class block(rpi_code_gen_object,python_code_gen_obejct):
    def __init__(self, label=None, input_block1=None,\
                 input_block1_name=None, \
                 variable_name=None, \
                 arduino_class=None, \
                 width=3, height=2, \
                 dt=0.002, \
                 num_inputs = 1, \
                 gui_input_labels=['Input 1'], \
                 set_input_func_names=['set_input_block1'], \
                 get_input_func_names=['get_input_block1_name'], \
                 fontdict = {'size': 20, 'family':'serif'}, \
                 placement_type=None, \
                 param_list=[],\
                 py_params=[], \
                 default_params={}, \
                 **kwargs):
        #print("in block.__init__")
        # how do I handle passing in placement and input params from a csv file?
        self.label = label
        self.variable_name = variable_name#used for code generation
        self.arduino_class = arduino_class
        self.fontdict = fontdict
        self.width = width
        self.height = height
        self.num_inputs = num_inputs
        self.gui_input_labels = gui_input_labels
        self.set_input_func_names = set_input_func_names
        self.get_input_func_names = get_input_func_names
        self.input_block1 = input_block1
        if input_block1 is not None:
            input_block1.output_block = self
        self.dt = dt
        self.input_block1_name = input_block1_name
        self.placement_type = placement_type
        self.param_list = param_list
        #print("in block.__init__, self.param_list = %s" % self.param_list)
        #
        # do py_params and param_list really serve two
        # different purposes?
        if (len(py_params) == 0) and (len(param_list) > 0):
            self.py_params = param_list
        else:
            self.py_params = py_params
        self.default_params = default_params
        # handle default placement kwargs from csv with default to None
        placement_args = ['abs_x','abs_y','rel_block_name','rel_pos','rel_distance',\
                          'xshift','yshift']
        for key in placement_args:
            if key in kwargs:
                value = value_from_str(kwargs[key])
            else:
                value = None
            setattr(self, key, value)

        if "loop_number" in kwargs:
            self.loop_number = int(kwargs['loop_number'])

        # I need a flag variable for no input blocks when setting
        # execution order
        self.no_input = False


    def isplaced(self):
        """Determine whether or not a block has beeen placed."""
        if self.placement_type is None:
            return False
        elif not hasattr(self, 'x'):
            return False
        elif not hasattr(self, 'y'):
            return False
        else:
            return True


    def _get_one_param_for_csv(self, param):
        """If block does not have an attribute names param, return an
        empty string.  If param is None, return an empty string.
        Else, return a string."""
        outstr = ""
        if hasattr(self, param):
            value = getattr(self, param)
            if value is not None:
                outstr = str(value)
        return outstr


    def _get_param_list_for_csv(self, attr_list):
        out_list = [self._get_one_param_for_csv(item) for item in attr_list]
        return out_list



    def get_type_name(self):
        # get the block type as a string (i.e. the name of the class without the module)
        return type(self).__name__


    def _get_position_csv_list(self):
        """Return a list of values associated with the position
        portion of the row that will be saved to csv."""
        N_rel = len(relative_attrs)
        N_abs = 2
        placement_type = self._get_one_param_for_csv("placement_type")
        if placement_type == "absolute":
            abs_list = [str(self.x), str(self.y)]
        else:
            abs_list = [""]*N_abs

        if placement_type == "relative":
            relative_list = self._get_param_list_for_csv(relative_attrs)
        else:
            relative_list = [""]*N_rel

        full_list = [placement_type] + abs_list + relative_list
        return full_list


    def get_csv_list_for_row(self):
        # Note: this method really gets a list, not a string for the row
        #
        # - what needs to be saved in order to recreate the block and
        #   the system model?
        # - how do I do this cleanly for the sake of inheritance?
        #     - how will block_with_two_inputs add onto this?
        #     - the csv file needs to be consistent for all blocks
        #         - so, everyone will have an input_block2_name,
        #           it will just be empty for some blocks
        #         - so, have a master list of parameters
        #         - if a block doesn't have an attr, return an empty string
        #         - this also needs to be true for abs vs relative position
        #             - leave abs_x and abs_y blank for relative placements
        #             - leave relative_block and friends blank for abs placements
        # Approach:
        # - build a list of parameters
        # - get the parameters as strings
        block_type = self.get_type_name()
        batch1_list = self._get_param_list_for_csv(csv_params_batch1)
        pos_list = self._get_position_csv_list()
        full_list = [block_type] + batch1_list + pos_list

        # get key:value csv pairs for the blocks param_list
        param_csv_list = get_param_key_value_csv_list(self)
        #print("param_csv_list = %s" % param_csv_list)
        N_params = len(param_csv_list)
        N_empty = max_csv_params - N_params
        full_list += param_csv_list + ['']*N_empty
        #print("in get_csv_list_for_row: %s" % full_list)
        #rowstr = ",".join(full_list)
        return full_list


    def get_python_secondary_init_code(self, Nstr="N"):
        #print("Nstr = %s" % Nstr)
        line1 = "%s.init_vectors(%s)" % (self.variable_name, Nstr)
        return [line1]


    def set_input_block1(self, input_block1):
        self.input_block1 = input_block1
        self.input_block1_name = self.input_block1.variable_name
        input_block1.output_block = self


    def get_attr_if_set(self, attr):
        """If the attribute attr is set and its bool it true, return it.
        Otherwise return None."""
        out = None
        val = None
        if hasattr(self, attr):
            val = getattr(self, attr)
            if val:
                out = val
        return val



    def get_input_block1_name(self):
        """Get the name of input block 1 if it is set."""
        attr = "input_block1_name"
        return self.get_attr_if_set(attr)


    def init_vectors(self, N=1000):
        # assuming that the default for most blocks will be to read
        # the inputs from their input_block1's and find their output
        self.output_vector = np.zeros(N)

    def get_arduino_loop_code(self):
        """Code to be executed in the Arduino loop method for the block"""
        # assumed form:
        # u.find_output(t_sec);
        pat = '%s.find_output(t_sec);'
        line1 = pat % self.variable_name
        return [line1]


    def define_edges(self):
        assert hasattr(self, 'x'), "blocks must be placed using place_absolute or place_relative before their edges can be defined."
        self.right_edge = (self.x + self.width/2, self.y)
        self.left_edge = (self.x - self.width/2, self.y)
        self.top_edge = (self.x, self.y + self.height/2)
        self.bottom_edge = (self.x, self.y - self.height/2)


    def place_absolute(self, x=None, y=None):
        """Set the x,y coordinates of the block explicitly"""
        if x is None:
            # typically there is one abs block and it is as 0,0
            # - fall back to that
            try:
                x = float(self.abs_x)
            except:
                x = 0

        if y is None:
            try:
                y = float(self.abs_y)
            except:
                y = 0

        self.x = x
        self.y = y
        # it seems weird that the attrs below were not getting set:
        self.abs_x = x
        self.abs_y = y
        self.define_edges()
        self.placement_type  = 'absolute'


    def switch_to_abs_placement(self):
        """Switch a block from relative to absolue placement,
        most likely because the block it was placed relative to
        has been deleted."""
        # as long as the block has self.x and self.y, this should be easy
        self.place_absolute(self.x, self.y)
        # set all relative placement attrs to None
        for attr in relative_attrs:
            setattr(self, attr, None)



    def _place_relative(self):
        pos_list = ['left', 'right', 'above', 'below']
        assert self.rel_pos in pos_list, 'In valid self.rel_pos string: %s' % self.rel_pos
        if self.rel_pos == 'right':
            self.x = self.rel_block.x + self.rel_distance
            self.y = self.rel_block.y
        elif self.rel_pos == 'left':
            self.x = self.rel_block.x - self.rel_distance
            self.y = self.rel_block.y
        elif self.rel_pos == 'above':
            self.x = self.rel_block.x
            self.y = self.rel_block.y + self.rel_distance
        elif self.rel_pos == 'below':
            self.x = self.rel_block.x
            self.y = self.rel_block.y - self.rel_distance

        self.x += self.xshift
        self.y += self.yshift
        self.define_edges()


    def place_relative(self, rel_block, rel_pos='right', rel_distance=4, xshift=0, yshift=0):
        """Set the x,y coordinates of the block relative to another block, rel_block.

        rel_pos refers to the position with respect to the rel_block, in must be a
        string in the list ['left', 'right', 'above', 'below']

        rel_distance refers to how far away the block is placed from the reference block.
        """
        self.placement_type  = 'relative'
        self.rel_block_name = rel_block.variable_name
        self.rel_block = rel_block
        self.rel_pos = rel_pos
        self.rel_distance = rel_distance
        self.xshift = xshift
        self.yshift = yshift

        self._place_relative()


    def update_relative_placement(self):
        if self.placement_type == 'relative':
            self._place_relative()


    def unplace_block(self):
        """Method called when the relative block that a block used as
        a reference is deleted."""
        if self.placement_type == 'relative':
           self.placement_type = None
           attr_list = ['rel_block_name','rel_pos','rel_distance']
           for attr in attr_list:
               setattr(self, attr, None)
           self.xshift = 0
           self.yshift = 0


    def change_rel_block_name(self, updated_block):
        """Used by the block_diagram method change_block_name when the
        name of a block is editted by the gui.

        It might be slightly awkward that the block and not the name
        are the input, but this is for consistancy with
        set_input_block1 and other methods called by change_block_name.

        So, the block variable_name must be set to the new name before
        passing it to this funciton."""
        self.rel_block_name = updated_block.variable_name


    def get_placememt_str(self):
        if self.placement_type is None:
            return ''
        else:
            if self.placement_type == 'absolute':
                place_str = 'abs;(%0.4g, %0.4g)' % (self.x, self.y)
                return place_str
            elif self.placement_type == 'relative':
                #self.rel_block_name = rel_block.variable_name
                #self.rel_pos = rel_pos
                #self.rel_distance = rel_distance
                #self.xshift = xshift
                #self.yshift = yshift

                place_str = 'rel; %s, %s, dist:%0.4g,shift:(%0.4g, %0.4g)' % \
                            (self.rel_block_name, self.rel_pos, self.rel_distance, \
                             self.xshift, self.yshift)
                return place_str


    def add_text(self, ax, point, text, xoffset=0, yoffset=0, \
                 fontdict=None, ha='center'):
        if fontdict is None:
            fontdict = self.fontdict
        ax.text(point[0]+xoffset, point[1]+yoffset, \
                text, fontdict=fontdict, \
                ha=ha, va='center')



    def place_label(self, ax):
        self.add_text(ax, (self.x, self.y), self.label)



    def draw_rectangle(self, ax):
        # need bottom left coordinates for mpl patch
        self.left = self.x - self.width/2
        self.bottom = self.y - self.height/2
        # Create a Rectangle patch
        rect = patches.Rectangle((self.left, self.bottom), self.width, self.height, \
                                 linewidth=1, edgecolor='k', facecolor='none')

        # Add the patch to the Axes
        ax.add_patch(rect)



    def draw_arrow(self, ax, start_x, start_y, dx, dy, \
                   lw=1, **plot_args):
        width = 0.01
        head_width = 15*width
        head_length = 2*head_width

        color, plot_args = get_wire_color(plot_args)
        fc = color
        ec = fc

        ax.arrow(start_x, start_y, dx, dy, \
                 lw=lw, fc=color, ec=ec, \
                 width=0.01, \
                 head_width=head_width, head_length=head_length, \
                 #overhang = self.ohg, \
                 length_includes_head=True, clip_on = False, \
                 **plot_args)


    def draw_arrow_se(self, ax, start_point, end_point, **kwargs):
        """Draw an arrow on axis ax from start_point to end_point.

        start_point and end_point are (x,y) pairs."""
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        dx = end_x - start_x
        dy = end_y - start_y
        self.draw_arrow(ax, start_x, start_y, dx, dy, **kwargs)


    def draw_segment_se(self, ax, start_point, end_point, **plot_args):
        """Draw an arrow on axis ax from start_point to end_point.

        start_point and end_point are (x,y) pairs."""
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        color, plot_args = get_wire_color(plot_args)
        # hard coded 'k-' is bad.....
        ax.plot([start_x, end_x], [start_y, end_y], color=color, \
                linestyle='-', **plot_args)



    def draw_L_segment_with_mid(self, ax, start_point, mid_point, \
            end_point, **plot_args):
        """Draw an L-shaped segment between start_point and end_point,
        assuming vertical first, then horizontal"""
        color, plot_args = get_wire_color(plot_args)
        start_x = start_point[0]
        start_y = start_point[1]
        mid_x = mid_point[0]
        mid_y = mid_point[1]
        end_x = end_point[0]
        end_y = end_point[1]
        ax.plot([start_x, mid_x], [start_y, mid_y], color=color, \
                linestyle='-', **plot_args)
        ax.plot([mid_x, end_x], [mid_y, end_y], color=color, \
                linestyle='-', **plot_args)


    def find_L_midpoint(self, start_point, end_point, style='vh'):
        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]

        if style == 'vh':
            mid_x = start_x
            mid_y = end_y
        elif style == 'hv':
            mid_x = end_x
            mid_y = start_y
        else:
            raise ValueError("style not understood: %s" % style)

        return (mid_x, mid_y)



    def draw_L_segment_vh(self, ax, start_point, end_point, **kwargs):
        """Draw an L-shaped segment between start_point and end_point,
        assuming vertical first, then horizontal"""
        mid_point = self.find_L_midpoint(start_point, end_point, 'vh')
        self.draw_L_segment_with_mid(ax, start_point, mid_point, end_point, **kwargs)


    def draw_L_segment_hv(self, ax, start_point, end_point, **kwargs):
        """Draw an L-shaped segment between start_point and end_point,
        assuming horizontal first, then vertical"""
        mid_point = self.find_L_midpoint(start_point, end_point, 'hv')
        self.draw_L_segment_with_mid(ax, start_point, mid_point, end_point, **kwargs)


    def clear_wire_start_and_end(self):
        if hasattr(self, 'wire_start'):
            self.wire_start = None
        if hasattr(self, 'wire_end'):
            self.wire_end = None


    def guess_wire_start(self, attr='input_block1'):
        """Try to guess where the input wire to the block starts based
        on comparing self.x and self.y to self.input_block1.x and
        self.input_block1.y and based on self.wire_style.  Either self.wire_style
        must be already specified or self.guess_wire_style must be called
        before calling this method.

        Only perform the guessing if self.wire_start is not specified
        (no attr) or is None."""

        # scenarios:
        # - self is purely left or right of input_block1: horizontal
        #     - start at left of right edge of input_block1 depending on whether self.x is
        #       larger or smaller than self.input_block1.x
        # - self is purely above or below input_block1: vertical
        #     - start at top or bottom of input_block1 depending self.y vs. self.input_block1.y
        # - self is shifted in both x and y from input_block1
        #     - cannot determine start without knowing wire style: 'vh' or 'hv'
        #         - can this style be guessed?
        #         - is assuming 'vh' bad for now?
        if hasattr(self, "wire_start"):
            if self.wire_start is not None:
                # guess is not needed
                return

        msg = "self.wire_style must be specified before calling self.guess_wire_start"
        assert hasattr(self, "wire_style"), msg
        assert self.wire_style is not None, msg

        myinput = getattr(self, attr)

        if self.wire_style[0] == 'h':
            # going horizontal first, start at left or right edge of self.input_block1
            if self.x > myinput.x:
                # block is right of input_block1
                myx = myinput.x + myinput.width*0.5
            else:
                # block is left of input_block1
                myx = myinput.x - myinput.width*0.5
            self.wire_start = (myx, myinput.y)
        elif self.wire_style[0] == 'v':
            # going horizontal first, start at left or right edge of myinput
            if self.y > myinput.y:
                # block is above input_block1
                myy = myinput.y + myinput.height*0.5
            else:
                # block is below input_block1
                myy = myinput.y - myinput.height*0.5
            self.wire_start = (myinput.x, myy)



    def guess_wire_end(self, attr='input_block1'):
        """Try to guess where the input wire ends.  Conceptually the
        same as guess_wire_start, but for the end of the wire.  See
        guess_wire_start help for more details."""
        if hasattr(self, "wire_end"):
            if self.wire_end is not None:
                # guess is not needed
                return

        myinput = getattr(self, attr)

        msg = "self.wire_style must be specified before calling self.guess_wire_end"
        assert hasattr(self, "wire_style"), msg
        assert self.wire_style is not None, msg
        if self.wire_style[-1] == 'h':
            # ending horizontal, stop at left or right edge of self
            if self.x > myinput.x:
                # block is right of input_block1, wire stops at left side of this block (self)
                myx = self.x - self.width*0.5
            else:
                # block is left of input_block1, wire stops at right side of this block (self)
                myx = self.x + self.width*0.5
            self.wire_end = (myx, self.y)
        elif self.wire_style[-1] == 'v':
            # end vertically, stop at top or bottom edge of self
            if self.y > myinput.y:
                # block is above input_block1
                myy = self.y - self.height*0.5
            else:
                # block is below input_block1
                myy = self.y + self.height*0.5
            self.wire_end = (self.x, myy)



    def guess_wire_style(self, attr='input_block1'):
        """Try to guess whether the wire needs to be purely
        horizontal, purely vertical, or both v and h based on
        comparing self.x and self.y to self.input_block1.x and self.input_block1.y.

        Only perform the guessing if self.wire_style is not specified
        (no attr) or is None."""

        # scenarios:
        # - self is purely left or right of input_block1: horizontal
        #     - start at left of right edge of input_block1 depending on whether self.x is
        #       larger or smaller than self.input_block1.x
        # - self is purely above or below input_block1: vertical
        #     - start at top or bottom of input_block1 depending self.y vs. self.input_block1.y
        # - self is shifted in both x and y from input_block1
        #     - cannot determine start without knowing wire style: 'vh' or 'hv'
        #         - can this style be guessed?
        #         - is assuming 'vh' bad for now?
        #             - note that for the summing junction with a Z^-1 block, we want 'hv'
        myinput = getattr(self, attr)
        if myinput is None:
            # do nothing
            return

        if hasattr(self, "wire_style"):
            if self.wire_style is not None:
                # guess is not needed
                return

        self.wire_delta_x = self.x - myinput.x
        self.wire_delta_y = self.y - myinput.y

        if np.abs(self.wire_delta_y) < 0.1:
            self.wire_style = 'h'
        elif np.abs(self.wire_delta_x) < 0.1:
            self.wire_style = 'v'
        else:
            self.wire_style = 'vh'


    def guess_output_direction(self):
        if hasattr(self, "outpur_dir"):
            if self.outpur_dir is not None:
                #do nothing
                return

        if not hasattr(self, "output_block"):
            # total guess, play the odds
            self.outpur_dir = "right"
        else:
            ox = self.output_block.x
            oy = self.output_block.y
            if ox > self.x:
                # assume no diagonal wires and normally horizontal first
                # - so, ignore vertical
                self.outpur_dir = "right"
            else:
                self.outpur_dir = "left"
        return self.outpur_dir


    def draw_input_wire(self, ax, attr='input_block1', **plot_args):
        print("in draw_input_wire, plot_args = %s" % plot_args)
        myinput = getattr(self, attr)
        if myinput is None:
            # do nothing
            return

        self.guess_wire_style(attr=attr)
        self.guess_wire_start(attr=attr)
        self.guess_wire_end(attr=attr)
        print("wire_style: %s" % self.wire_style)

        # drawing a purely 'h' or 'v' wire is simpler than drawing 'hv' or 'vh'
        # - one segment vs. two
        # we need four things: start_x, start_y, dx, dy
        if len(self.wire_style) == 1:
            # purely vertical or horizontal
            print('len=1')
            self.draw_arrow_se(ax, self.wire_start, self.wire_end, **plot_args)
        else:
            # - so far, we have two options: 'vh' or 'hv'
            # - approach:
            #     - plot line from start to midpoint
            #     - draw arrow from midpoint to end
            color, plot_args = get_wire_color(plot_args)
            if self.wire_style == 'vh':
                # midpoint is above or below start and left or right of end
                # - x is the same as the start and y is the same as the end
                midpoint = (self.wire_start[0],self.wire_end[1])
            elif self.wire_style == 'hv':
                # the opposite case as 'vh':
                midpoint = (self.wire_end[0],self.wire_start[1])
            print("color = %s" % color)
            ax.plot([self.wire_start[0], midpoint[0]], \
                    [self.wire_start[1], midpoint[1]], color=color, linestyle='-')#<-- this is draw_segment_se
            self.draw_arrow_se(ax, midpoint, self.wire_end, color=color, **plot_args)
        ##!## old, less general code:
        ## delta_x = self.x - myinput.x
        ## delta_y = self.y - myinput.y

        ## if np.abs(delta_y) < 0.25:
        ##     # horizontal wire
        ##     # - assuming right to left
        ##     #    - could check later with self.x vs myinput.x
        ##     start_x = myinput.x + myinput.width*0.5
        ##     stop_x = self.x - self.width*0.5
        ##     dx = stop_x - start_x
        ##     start_y = myinput.y
        ##     dy = self.y - myinput.y
        ## else:
        ##     # assuming vertical up
        ##     start_y = myinput.y + myinput.height*0.5
        ##     stop_y = self.y - self.height*0.5
        ##     dy = stop_y - start_y
        ##     start_x = myinput.x
        ##     dx = self.x - myinput.x



    def draw(self, ax, wire_color='k'):
        print("%s, wire_color = %s" % (self.variable_name, wire_color))
        self.place_label(ax)
        self.draw_rectangle(ax)
        self.draw_input_wire(ax, wire_color=wire_color)


    def get_output(self, i):
        raise NotImplementedError

class no_input_block(block):
    """A class of blocks that have no inputs (sources, loop counters, time, ...)"""
    def __init__(self, *args, **kwargs):
        block.__init__(self, *args, **kwargs)
        self.num_inputs = 0
        self.no_input = True


class no_box_block(block):
    def draw(self, ax, **kwargs):
        # draw can be passed a wire color that should be ignored
        self.place_label(ax)


class source_block(no_input_block):
    """Block for step inputs or fixed sine input or swept inputs or
    other signals that are given as inputs to a system"""
    pass


class block_with_nISR_input(block):
    def get_arduino_loop_code(self):
        """assuming nISR is a global variable on the Arduino side that
        is incremented in a timing ISR.  This is analogous to the loop
        counting variable in Python"""
        # assumed form:
        # u.find_output(t_sec);
        pat = '%s.find_output(nISR);'
        line1 = pat % self.variable_name
        return [line1]


    def get_rpi_loop_code(self):
        pat = '%s.find_output(i);'
        line1 = pat % self.variable_name
        return [line1]




class loop_count_block(block_with_nISR_input, \
                       arduino_code_gen_no_params, \
                       #no_input_block):
                       source_block):
    """Block that gives access to the loop counter and behaves like a
    block"""
    def __init__(self, variable_name="lp_cnt_block", \
                 arduino_class="loop_count_block", \
                 width=10, **kwargs):
        print("\n"*3)
        print("start of loop_count_block.__init__, width = %s" % width)
        print("\n"*3)

        if "label" in kwargs:
            label = kwargs.pop('label')
        else:
            label="loop count"
        block_with_nISR_input.__init__(self, label=label, variable_name=variable_name, \
                                       arduino_class=arduino_class, \
                                       width=width, **kwargs)
        self.arduino_class = arduino_class

        self.no_input = True
        print("\n"*3)
        print("end of loop_count_block.__init__, width = %s" % width)
        print("\n"*3)


    def find_output(self, i):
        """This is just making the loop counter act like a block"""
        self.output_vector[i] = i
        return self.output_vector[i]




class block_with_one_input_setup_code(block):
    """A class for blocks that need to attach their input_block1 in the
    Arduino setup code."""
    def get_arduino_setup_code(self):
        # G.set_input(&Dz);
        input_block1_line = "%s.set_input_block1(&%s);" % (self.variable_name, \
                                                           self.input_block1.variable_name)
        return [input_block1_line]


    def get_python_secondary_init_code(self, Nstr="N"):
        # me.input = myinput
        print("Nstr = %s" % Nstr)
        line1 = "%s.set_input_block1(%s)" % (self.variable_name, self.input_block1.variable_name)
        line2 = "%s.init_vectors(%s)" % (self.variable_name, Nstr)
        return [line1, line2]


class arduino_plant(no_code_python_block, block_with_one_input_setup_code):
    """If information is sent to an Arduino block using i2c, spi, or
    serial and sensor data is read from the Arduino using i2c, spi, or
    serial, then the plant block doesn't actually need to do anything
    in terms of Python code (all of its get python code methods return
    empty lists)."""
    pass


def_width_1 = 3
def_height_1 = 3

class int_constant_block(arduino_code_gen_loop_no_inputs, source_block):
    def __init__(self, value=100, variable_name=None, \
                 arduino_class="int_constant_block", \
                 width=def_width_1, height=def_height_1, \
                 param_list=['value'], \
                 py_params=['value'], \
                 default_params={'value':100},
                 **kwargs):
        if "label" not in kwargs:
            label = str(value)
            kwargs["label"] = label
        no_input_block.__init__(self, variable_name=variable_name, \
                                width=width, height=height, param_list=param_list, \
                                 py_params=py_params, \
                                 default_params=default_params, **kwargs)
        self.value = value
        self.arduino_class = arduino_class


    def find_output(self, i):
        """This is just making the loop counter act like a block"""
        self.output_vector[i] = self.value
        return self.value


    def _get_arduino_param_str(self):
        # h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin */
        params = "%s" % self.value
        self._arduino_param_str = params
        return self._arduino_param_str


class float_constant_block(int_constant_block):
    def __init__(self, value=100, variable_name=None, \
                 arduino_class="float_constant_block", \
                 width=def_width_1, height=def_height_1, \
                 param_list=['value'], \
                 py_params=['value'], \
                 default_params={'value':100},
                 **kwargs):
        if "label" not in kwargs:
            label = str(value)
            kwargs["label"] = label
        no_input_block.__init__(self, variable_name=variable_name, \
                                width=width, height=height, param_list=param_list, \
                                 py_params=py_params, \
                                 default_params=default_params, **kwargs)
        self.value = value
        self.arduino_class = arduino_class




class output_block(arduino_code_gen_loop_no_inputs, \
                   block_with_one_input_setup_code, \
                   no_code_python_block,no_box_block):
    """Assuming for now that an output block has no Arduino code
    associated with it

    - what do my students want output blocks to do?
        - I think they want something that looks like my conceptual
          block diagrams especially for open-loop systems
          - the output needs to go somewhere

    - should an output block be assumed to be a print block?
    - the output block reads its input and has only one input
        - does it need to be in a certain list to allow its input to be
          set by the gui?


    Steps to a useful output block:
    - set input
    - place
    - draw
    - generate code
    """
    def __init__(self, \
                 input_block1=None, \
                 label='$Y(s)$', \
                 variable_name='bd_output', \
                 arduino_class='output_block', \
                 param_list=[], \
                 default_params={}, \
                 py_params=[], **kwargs):
        block.__init__(self, label=label, \
                       input_block1=input_block1, \
                       variable_name=variable_name, \
                       arduino_class=arduino_class, \
                       param_list=param_list, \
                       default_params=default_params, \
                       py_params=py_params, \
                       **kwargs, \
                       )



    def draw(self, ax, **kwargs):
        self.place_label(ax)
        self.draw_input_wire(ax)


    def _get_arduino_param_str(self):
        # must set the variable self._arduino_param_str
        self._arduino_param_str = ""
        return self._arduino_param_str


#    def get_arduino_setup_code(self):
#        return []
#
#
#    def get_arduino_init_code(self):
#        return []
#
#
#    def get_arduino_loop_code(self):
#        return []
#
#    def get_arduino_print_code(self):
#        return []
#


class step_input(source_block,no_box_block):
    def __init__(self, label='$U(s)$', on_time=0.1, \
                 amp=100, \
                 input_block1=None, \
                 variable_name='u_step_block', \
                 arduino_class='step_input', \
                 py_params=['on_time','amp'], \
                 param_list=['on_time','amp'], \
                 default_params={'on_time':0.1, 'amp':100}, **kwargs):
        source_block.__init__(self, label=label, input_block1=input_block1, \
                             variable_name=variable_name, param_list=param_list, \
                              default_params=default_params, \
                              **kwargs)
        self.on_time = on_time
        self.amp = amp
        self.arduino_class = arduino_class
        self.on_index = int(self.on_time/self.dt)#<-- dt is set in the block.__init__
        self.py_params = py_params


    def _get_arduino_param_str(self):
        pat = '%0.4g, %i'
        params = pat % (self.on_time, self.amp)
        self._arduino_param_str = params
        return self._arduino_param_str


    def find_output(self, i):
        if i < self.on_index:
            self.output_vector[i] = 0
        else:
            self.output_vector[i] = self.amp
        return self.output_vector[i]


class sloped_step(step_input):
    def __init__(self, label='$U_{sloped}(s)$', on_time=0.1, \
                 amp=100, \
                 slope=1, \
                 input_block1=None, \
                 variable_name='u_sloped_step', \
                 arduino_class='sloped_step', \
                 py_params=['on_time','amp','slope'], \
                 param_list=['on_time','amp','slope'], \
                 default_params={'on_time':0.1, 'amp':100, 'slope':1}, **kwargs):
        step_input.__init__(self, amp=amp, on_time=on_time, \
                            label=label, input_block1=input_block1, \
                            arduino_class=arduino_class, \
                            variable_name=variable_name, param_list=param_list, \
                            py_params=py_params, \
                            default_params=default_params, \
                            **kwargs)
        self.slope = slope


    def _get_arduino_param_str(self):
        #float switch_on_time=0.1, float myslope=1, int AMP=
        pat = '%0.4g, %0.4g, %i'
        params = pat % (self.on_time, self.slope, self.amp)
        self._arduino_param_str = params
        return self._arduino_param_str



class pulse_input(step_input):
    def __init__(self, label='$U_{pulse}(s)$', on_time=0.1, \
                 off_time=0.5, \
                 amp=100, \
                 input_block1=None, \
                 variable_name='u_pulse_block', \
                 arduino_class='pulse_input', \
                 py_params=['on_time','off_time','amp'], \
                 param_list=['on_time','off_time','amp'], \
                 default_params={'on_time':0.1, 'off_time':1, 'amp':100}, \
                 **kwargs):
        source_block.__init__(self, label=label, input_block1=input_block1, \
                             variable_name=variable_name, \
                              param_list=param_list, default_params=default_params, \
                              **kwargs)
        self.on_time = on_time
        self.off_time = off_time
        self.amp = amp
        self.arduino_class = arduino_class
        self.on_index = int(self.on_time/self.dt)#<-- dt is set in the block.__init__
        self.off_index = int(self.off_time/self.dt)
        self.py_params = py_params


    def _get_arduino_param_str(self):
        pat = '%0.4g, %0.4g, %i'
        params = pat % (self.on_time, self.off_time, self.amp)
        self._arduino_param_str = params
        return self._arduino_param_str


    def find_output(self, i):
        if ((i >= self.on_index) and (i <= self.off_index)) :
            self.output_vector[i] = self.amp
        else:
            self.output_vector[i] = 0
        return self.output_vector[i]

class fixed_sine_input(source_block,no_box_block):
    """Note: I am assuming that my final goals are either Arduino or RPi C.  I
    am not supporting Python execution anymore."""
    def __init__(self, label='$U_{fixed sine}(s)$',
                 freq=1, \
                 amp=100, \
                 input_block1=None, \
                 variable_name='u_fixed_sine', \
                 arduino_class='fixed_sine_input', \
                 py_params=['freq','amp'], \
                 param_list=['freq','amp'], \
                 default_params={'freq':1, 'amp':100}, **kwargs):
        source_block.__init__(self, label=label, input_block1=input_block1, \
                             variable_name=variable_name, param_list=param_list, \
                              default_params=default_params, \
                              **kwargs)
        self.freq = freq
        self.amp = amp
        self.arduino_class = arduino_class
        self.py_params = py_params


    def _get_arduino_param_str(self):
        pat = '%0.4g, %i'
        params = pat % (self.freq, self.amp)
        self._arduino_param_str = params
        return self._arduino_param_str




class swept_sine_input(fixed_sine_input):
    """Note: I am assuming that my final goals are either Arduino or RPi C.  I
    am not supporting Python execution anymore."""
    def __init__(self, label='$U_{swept sine}(s)$',
                 slope=0.1, \
                 amp=100, \
                 dead_time = 1.0, \
                 input_block1=None, \
                 variable_name='u_swept_sine', \
                 arduino_class='swept_sine_input', \
                 py_params=['slope','amp','dead_time'], \
                 param_list=['slope','amp','dead_time'], \
                 default_params={'slope':0.1, 'amp':100, 'dead_time':1}, \
                 **kwargs):
        source_block.__init__(self, label=label, input_block1=input_block1, \
                             variable_name=variable_name, param_list=param_list, \
                              default_params=default_params, \
                              **kwargs)
        self.slope = slope
        self.amp = amp
        self.dead_time = dead_time
        self.arduino_class = arduino_class
        self.py_params = py_params


    def _get_arduino_param_str(self):
        pat = '%0.4g, %0.4g, %0.4g'
        params = pat % (self.slope, self.amp, self.dead_time)
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_arduino_menu_code(self):
        #   enc.encoder_count = 0;
        line1 = "%s.set_t_on(1);" % self.variable_name
        line2 = "%s.set_t_off(stop_t);" % self.variable_name
        return [line1, line2]



class saturation_block(block_with_one_input_setup_code):
    def __init__(self, label='sat', \
                 input_block1=None, \
                 mymax=255, \
                 variable_name='sat_block', \
                 arduino_class='saturation_block', \
                 py_params=['mymax'], \
                 params=['mymax'], \
                 default_params={'mymax':255}, \
                 **kwargs):
        block_with_one_input_setup_code.__init__(self, label=label, input_block1=input_block1, \
                                                 variable_name=variable_name, **kwargs)
        self.arduino_class = arduino_class
        self.mymax = mymax
        self.py_params = py_params


    def _get_arduino_param_str(self, include_inputs=False):
        #saturation_block sat_block = saturation_block(&Dz);
        if include_inputs:
            params = "&%s" % self.input_block1.variable_name
        else:
            params = ""
        self._arduino_param_str = params
        return self._arduino_param_str



    def find_output(self, i):
        raw_in = self.input_block1.output_vector[i]
        if raw_in > self.mymax:
            cur_out = self.mymax
        elif raw_in < -self.mymax:
            cur_out = -self.mymax
        else:
            cur_out = raw_in
        self.output_vector[i] = cur_out
        return self.output_vector[i]




class sat2_adjustable_block(saturation_block):
    """A saturation block whose min and max can be set my the code"""
    def __init__(self, mymax=255, \
                 mymin=None, \
                 label='sat2', \
                 input_block1=None, \
                 variable_name='sat2_block', \
                 arduino_class='sat2_adjustable_block', \
                 py_params=['mymax','mymin'], \
                 param_list=['mymax'], \
                 default_params={'mymax':255}, \
                 **kwargs):
        saturation_block.__init__(self, label=label, input_block1=input_block1, \
                                  variable_name=variable_name, param_list=param_list, \
                                  default_params=default_params, **kwargs)
        self.arduino_class = arduino_class
        if not mymax:
            mymax = 255
        self.mymax = mymax
        if mymin is None:
            mymin = -mymax
        self.mymin = mymin
        self.py_params = py_params



    def _get_arduino_param_str(self):
        #saturation_block sat_block = saturation_block(&Dz);
        params = "%i, %i" % (int(self.mymax), int(self.mymin))
        self._arduino_param_str = params
        return self._arduino_param_str


    def find_output(self, i):
        raw_in = self.input_block1.output_vector[i]
        if raw_in > self.mymax:
            cur_out = self.mymax
        elif raw_in < self.mymin:
            cur_out = self.myin
        else:
            cur_out = raw_in
        self.output_vector[i] = cur_out
        return self.output_vector[i]


class block_with_two_inputs(block):
    def __init__(self, label=None, \
                 input_block1=None, input_block2=None, \
                 arduino_class='class_not_specified', \
                 variable_name='var_name_not_specified', \
                 input_block1_name=None, \
                 input_block2_name=None, \
                 width=3, \
                 height=2, \
                 num_inputs = 2, \
                 gui_input_labels=['Input 1','Input 2'], \
                 set_input_func_names=['set_input_block1', \
                                       'set_input_block2'], \
                 get_input_func_names=['get_input_block1_name', \
                                       'get_input_block2_name'], \
                 py_params=[], **kwargs):
        if "variable_name" in kwargs:
            variable_name = kwargs.pop('variable_name')

        if "param_list" not in kwargs:
            kwargs["param_list"] = copy.copy(py_params)

        block.__init__(self,label=label, arduino_class=arduino_class, \
                       variable_name=variable_name, \
                       input_block1_name=input_block1_name, \
                       num_inputs=num_inputs, \
                       gui_input_labels=gui_input_labels, \
                       set_input_func_names=set_input_func_names, \
                       get_input_func_names=get_input_func_names, \
                       width=width, height=height, **kwargs)
        print("in block_with_two_inputs.__init__, kwargs = %s" % kwargs)
        self.input_block1 = input_block1
        self.input_block2 = input_block2
        self.input_block2_name = input_block2_name
        self.py_params = py_params
        self.waypoints1 = []
        self.waypoints2 = []


    def get_input_block2_name(self):
        """Get the name of input block 2 if it is set."""
        attr = "input_block2_name"
        return self.get_attr_if_set(attr)



    def get_arduino_setup_code(self):
        # G.set_input(&Dz);
        input_block1_line = "%s.set_input_blocks(&%s, &%s);" % (self.variable_name, \
                                                               self.input_block1.variable_name, \
                                                               self.input_block2.variable_name)
        return [input_block1_line]


    ## def set_input_block1(self, input_block1):
    ##     self.input_block1 = input_block1
    ##     input_block1.output_block = self


    def set_input_block2(self, input_block2):
        self.input_block2 = input_block2
        self.input_block2_name = self.input_block2.variable_name
        input_block2.output_block = self


    def set_inputs(self, input_block1, input_block2):
        self.set_input_block1(input_block1)
        self.set_input_block2(input_block2)


    def _draw_input_wire(self, ax, sign=1, inblock='input_block1', yoffset=0, \
                         style='hv', waypoints=[], in_shift=0.5, **kwargs):
        # - I need to draw better wires than the summing junction
        #   defaults
        # - unlike a summing junction, I want to hard code
        #   two inputs on the left and one output on the right
        #     - do I care how the wires exit the input block?

        # wire1 ends on the top(sign=1) or bottom(sign=-1) left
        end_point = (self.x - self.width/2, self.y + yoffset*sign)
        # wire1 must come in horizontally
        in_point = (end_point[0] - in_shift, end_point[1])#<-- setting this
                                                     #shift to the
                                                     #same thing for wire 1 and 2 causes issues

        # where does the wire start?
        # - assume output right?
        #start_point = find_start_point(self.input_block1, self, wire_style[0])


        start_block = getattr(self, inblock)
        ## If start_block is not placed, I need to exit gracefully
        if not start_block.isplaced():
            print("start block not placed, wire cannot be drawn")
            # exit
            return None

        if hasattr(start_block, 'right_edge'):
            start_point = start_block.right_edge
        else:
            start_point = (start_block.x, start_block.y)

        out_point = (start_point[0] + 0.25, start_point[1])

        ### old way:
        ## self.draw_segment_se(ax, start_point, out_point)
        ## if style == 'hv':
        ##     self.draw_L_segment_hv(ax, out_point, midpoint)
        ## else:
        ##     self.draw_L_segment_vh(ax, out_point, midpoint)
        ## self.draw_arrow_se(ax, midpoint, end_point)

        ## New way with waypoints:
        # - I think the old way basically does this:
        #     - [start_point, out_point, midpoint, end_point]
        # - so, out_point and midpoint are basically waypoints
        #     - out_point is before any other way points and midpoint is after (poor name)
        all_waypoints = [out_point] + waypoints + [in_point]
        draw_wire(ax, start_point, end_point, waypoints=all_waypoints, \
                  L_style=style, **kwargs)


    def draw_input1_wire(self, ax, color='k'):
        if hasattr(self, "waypoints1"):
            waypoints = self.waypoints1
        else:
            waypoints = []
        self._draw_input_wire(ax, sign=1, inblock='input_block1', yoffset=self.height*0.3, \
                              waypoints=waypoints, color=color)


    def draw_input2_wire(self, ax, color='k'):
        if hasattr(self, "waypoints2"):
            waypoints = self.waypoints2
        else:
            waypoints = []
        self._draw_input_wire(ax, sign=-1, inblock='input_block2', yoffset=self.height*0.3, \
                              waypoints=waypoints, in_shift=1, color=color)


    def add_waypoint1(self, point):
        self.waypoints1.append(point)


    def add_waypoint2(self, point):
        self.waypoints2.append(point)



    def draw(self, ax, wire_color='k'):
        #block.draw(self, ax)
        self.place_label(ax)
        self.draw_rectangle(ax)
        if self.input_block1 is not None:
            self.draw_input1_wire(ax, color=wire_color)

        if self.input_block2 is not None:
            self.draw_input2_wire(ax, color=wire_color)



    def get_python_secondary_init_code(self, Nstr="N"):
        # me.input = myinput
        print("Nstr = %s" % Nstr)
        line1 = "%s.set_input_block1(%s)" % (self.variable_name, self.input_block1.variable_name)
        line2 = "%s.set_input_block2(%s)" % (self.variable_name, self.input_block2.variable_name)
        line3 = "%s.init_vectors(%s)" % (self.variable_name, Nstr)
        return [line1, line2, line3]




class summing_junction(block_with_two_inputs):
    def define_edges(self):
        print('=='*5)
        print('\n'*3)
        print("in summing_junction define_edges")

        block_with_two_inputs.define_edges(self)

        print("at top, self.bottom_edge:")
        print(self.bottom_edge)
        myy = self.bottom_edge[1] + self.fb_vertical_offset -1
        myx = self.bottom_edge[0]
        self.bottom_edge = (myx, myy)
        print("self.bottom_edge = ")
        print(self.bottom_edge)


    def __init__(self, input_block1=None, input_block2=None, radius=1, \
                 arduino_class='summing_junction', \
                 variable_name='sum1_block', \
                 fontdict = {'size': 16, 'family':'serif'}, \
                 draw_feedback_loop=True, \
                 fb_vertical_offset=-3, \
                 py_params=['fb_vertical_offset'], \
                 param_list=['fb_vertical_offset'], \
                 default_params={'fb_vertical_offset':-3}, \
                 **kwargs):
        block_with_two_inputs.__init__(self, input_block1=input_block1, \
                                       input_block2=input_block2, \
                                       arduino_class=arduino_class, \
                                       variable_name=variable_name, \
                                       py_params=py_params, param_list=param_list, \
                                       default_params=default_params, **kwargs)

        self.radius = radius
        self.width = self.radius*2#used for drawing wires
        self.height = self.radius*2#used for drawing wires
        self.input_block1 = input_block1
        self.input_block2 = input_block2
        if input_block1 is not None:
            input_block1.output_block = self
        if input_block2 is not None:
            input_block2.output_block = self

        self.fontdict = fontdict
        self.draw_feedback_loop = draw_feedback_loop
        self.arduino_class = arduino_class
        self.variable_name = variable_name
        self.py_params = py_params
        self.fb_vertical_offset = fb_vertical_offset


    ## def set_input_block1(self, input_block1):
    ##     self.input_block1 = input_block1
    ##     input_block1.output_block = self


    def set_input_block2(self, input_block2):
        self.input_block2 = input_block2
        self.input_block2_name = self.input_block2.variable_name
        input_block2.output_block = self


    def set_inputs(self, input_block1, input_block2):
        self.set_input_block1(input_block1)
        self.set_input_block2(input_block2)


    def _get_arduino_param_str(self, include_inputs=False):
        #summing_junction sum1 = summing_junction(&u, &G);

        # - sometimes the input blocks haven't been created yet and
        #   will need to be set in the setup code
        #     - include_inputs is True only if the inputs already exist and
        #       pointers can be used during the init code

        if include_inputs:
            pat = '&%s, &%s'
            params = pat % (self.input_block1.variable_name, self.input_block2.variable_name)
        else:
            params = ''
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_python_secondary_init_code(self, Nstr="N"):
        print("Nstr = %s" % Nstr)
        line1 = "%s.input_block1 = %s" % (self.variable_name, self.input_block1.variable_name)
        line2 = "%s.input_block2 = %s" % (self.variable_name, self.input_block2.variable_name)
        line3 = "%s.init_vectors(%s)" % (self.variable_name, Nstr)
        return [line1, line2, line3]


    def get_arduino_setup_code(self):
        # sum1.set_inputs(&u, &G);
        input_line = "%s.set_inputs(&%s, &%s);" % \
                     (self.variable_name, \
                      self.input_block1.variable_name, \
                      self.input_block2.variable_name)
        return [input_line]


    def find_output(self, i):
        output_i = self.input_block1.output_vector[i] - self.input_block2.output_vector[i]
        self.output_vector[i] = output_i
        return self.output_vector[i]


    def draw_circle(self, ax):
        cir = patches.Circle((self.x, self.y), radius=self.radius, \
                             linewidth=1, edgecolor='k', facecolor='none')
        ax.add_patch(cir)


    def draw_input1_wire(self, ax, **kwargs):
        self.draw_input_wire(ax, attr='input_block1', **kwargs)


    def add_radial_text(self, ax, text, angle, rfactor=1.85, fontdict=None):
        R = self.radius*rfactor
        angle_rad = angle*np.pi/180
        x = R*np.cos(angle_rad) + self.x
        y = R*np.sin(angle_rad) + self.y
        point = (x,y)
        self.add_text(ax, point, text, fontdict=fontdict)


    def add_pos_label(self, ax):
        self.add_radial_text(ax, '+', 150)


    def add_neg_label(self, ax):
        self.add_radial_text(ax, '-', -65, fontdict = {'size': 20, 'family':'serif'})


    def draw_feedback_wire(self, ax, start_x_offset=1, start_y_offset=0, **kwargs):
        print("calling draw_feedback_wire")
        # - how do I clean this up and allow for waypoints?
        # - plan:
        #     - final waypoint is at (end_x, end_y + self.fb_vertical_offset)
        #     - first waypoint is to the right of the starting block
        #     - allow other waypoints
        #     - call my new function: draw_wire
        assert self.input_block2 is not None, "must specify input_block2 before drawing feedback wire"


        #start_x = self.input_block2.x + self.input_block2.width*0.5 + start_x_offset
        start_x = self.input_block2.x + self.input_block2.width*0.5
        start_y = self.input_block2.y + start_y_offset
        start_point = (start_x, start_y)

        end_x = self.x
        end_y = self.y - self.radius
        end_point = (end_x, end_y)

        ### old way:
        ## mid_y = start_y + self.fb_vertical_offset
        ## ax.plot([start_x, start_x, end_x],[start_y, mid_y, mid_y], 'k-')
        ## dx = 0
        ## dy = end_y - mid_y
        ## self.draw_arrow(ax, end_x, mid_y, dx, dy)

        ### new way:
        first_way_pt = (start_x + start_x_offset, start_y)
        final_way_y = end_y + self.fb_vertical_offset
        final_way_pt = (end_x, final_way_y)
        #ax.plot([end_x],[final_way_y],'k^')
        #ax.plot([start_x],[start_y],'b^')
        #ax.plot([end_x],[end_y],'r^')


        self.all_waypoints2 = [first_way_pt] + self.waypoints2 + [final_way_pt]
        print("all_waypoints2: %s" % self.all_waypoints2)
        draw_wire(ax, start_point, end_point, waypoints=self.all_waypoints2,**kwargs)#, L_style='vh', **plot_args)


    def draw_input2_wire(self, ax, wire_style='hv', **kwargs):
        # Ideally: draw a wire from input_block2 left edge to bottom of
        # self, going left first, then up
        # - how do I do this using code written above?

        # new approach:
        # - separate the code in draw_input_wire to
        #     - plot a segment (wire with no arrow)
        #     - find midpoint
        #     - plot arrow from midpoint to end
        # - find start, end, and midpoint in this function
        # - pass start and midpoint to plot segment
        # - pass midpoint and end to plot arrow
        # - function draw_arrow_se already exists
        # - create function to draw segment


        # these are not quite right and should depend on wire_style
        #import pdb
        #pdb.set_trace()
        start_point = find_start_point(self.input_block2, self, wire_style[0])
        end_point = find_end_point(self.input_block2, self, wire_style[1])
        midpoint = find_midpoint(start_point, end_point, wire_style=wire_style)
        self.draw_segment_se(ax, start_point, midpoint, **kwargs)
        self.draw_arrow_se(ax, midpoint, end_point, **kwargs)


    def draw(self, ax, **kwargs):
        self.draw_circle(ax)
        if self.input_block1 is not None:
            self.draw_input1_wire(ax, **kwargs)
        if self.draw_feedback_loop:
            if self.input_block2 is not None:
                self.draw_feedback_wire(ax, **kwargs)
        self.add_pos_label(ax)
        self.add_neg_label(ax)


class logic_block(arduino_code_gen_loop_no_inputs, block):
    pass


class logic_block_no_params(logic_block):
    def _get_arduino_param_str(self):
        self._arduino_param_str = ""
        return ""


class switch_block(block_with_one_input_setup_code, logic_block_no_params):
    def __init__(self, *args, label="switch", \
                 arduino_class="switch_block", \
                 width=7, \
                 **kwargs):
        block.__init__(self, *args, label=label, \
                       arduino_class=arduino_class, \
                       width=width, \
                       **kwargs)


    def get_arduino_menu_code(self):
        #  turn switch off at start of test
        line1 = "%s.output = 0;" % self.variable_name
        return [line1]


class abs_block(block_with_one_input_setup_code, logic_block_no_params):
    def __init__(self, *args, label="abs", \
                 arduino_class="abs_block", \
                 width=7, \
                 **kwargs):
        block.__init__(self, *args, label=label, \
                       arduino_class=arduino_class, \
                       width=width, \
                       **kwargs)


class prev_hold_block(abs_block):
    def __init__(self, *args, label="prev", \
                 arduino_class="prev_hold_block", \
                 width=7, \
                 **kwargs):
        abs_block.__init__(self, *args, label=label, \
                       arduino_class=arduino_class, \
                       width=width, \
                       **kwargs)




class two_input_math_and_logic_block(logic_block_no_params, block_with_two_inputs):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='greater_than_block', \
                 variable_name='gt_block', \
                 width=def_width_1, height=def_height_1, \
                 param_list=[], \
                 default_params={}, \
                 defaut_label='%', \
                 **kwargs):
        block_with_two_inputs.__init__(self, input_block1=input_block1, input_block2=input_block2, \
                                  arduino_class=arduino_class, \
                                  variable_name=variable_name, \
                                  param_list=param_list, \
                                  default_params=default_params, \
                                  defaut_label=defaut_label, \
                                  **kwargs)
        self.width = width
        self.height = height
        if "label" in kwargs:
            label = kwargs['label']
        else:
            label = defaut_label
        self.label = label


class greater_than_block(two_input_math_and_logic_block):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='greater_than_block', \
                 variable_name='gt_block', \
                 width=def_width_1, height=def_height_1, \
                 param_list=[], \
                 default_params={}, \
                 **kwargs):
        two_input_math_and_logic_block.__init__(self, \
                        input_block1=input_block1, input_block2=input_block2, \
                        arduino_class=arduino_class, \
                        variable_name=variable_name, \
                        param_list=param_list, \
                        default_params=default_params, \
                        defaut_label='>', \
                        **kwargs)


    def find_output(self, i):
        output_i = self.input_block1.output_vector[i] > self.input_block2.output_vector[i]
        self.output_vector[i] = int(output_i)
        return self.output_vector[i]


class less_than_block(two_input_math_and_logic_block):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='less_than_block', \
                 variable_name='lt_block', \
                 width=def_width_1, height=def_height_1, \
                 param_list=[], \
                 default_params={}, \
                 **kwargs):
        two_input_math_and_logic_block.__init__(self, \
                        input_block1=input_block1, input_block2=input_block2, \
                        arduino_class=arduino_class, \
                        variable_name=variable_name, \
                        param_list=param_list, \
                        default_params=default_params, \
                        defaut_label='<', \
                        **kwargs)


class and_block(two_input_math_and_logic_block):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='and_block', \
                 variable_name='andBlock', \
                 width=def_width_1, height=def_height_1, \
                 param_list=[], \
                 default_params={}, \
                 **kwargs):
        two_input_math_and_logic_block.__init__(self, \
                        input_block1=input_block1, input_block2=input_block2, \
                        arduino_class=arduino_class, \
                        variable_name=variable_name, \
                        param_list=param_list, \
                        default_params=default_params, \
                        defaut_label='and', \
                        **kwargs)



class or_block(two_input_math_and_logic_block):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='or_block', \
                 variable_name='orBlock', \
                 width=def_width_1, height=def_height_1, \
                 param_list=[], \
                 default_params={}, \
                 **kwargs):
        two_input_math_and_logic_block.__init__(self, \
                        input_block1=input_block1, input_block2=input_block2, \
                        arduino_class=arduino_class, \
                        variable_name=variable_name, \
                        param_list=param_list, \
                        default_params=default_params, \
                        defaut_label='or', \
                        **kwargs)


class loop_variable(block_with_one_input_setup_code):
    # This class makes no sense to me.  What was I thinking?
    # - how is this different from loop_count?
    # - why would I need a loop_variable with an input?
    # - following the bunny trail, I guess this was part of my
    #   thinking for multiple loops running at different digital frequencies
    #   - I abandoned that idea, so I probably shouldn't use this class....
    def find_output(self, j):
        """This is just making the loop counter act like a block.
        This should be overwritten by all derived blocks."""
        value = self.input_block1.read_output(j)
        self.output_vector[j] = value
        self.value = value#<-- set for reading in the read_output
            #method, regardless of loop index i or j (fast loop or slow)
        return self.value


    def read_output(self, i):
        """The loop index i could be from either loop and must be
        ignored.  But it must be accepted, because that is how all
        blocks retrieve their input(s)."""
        return self.value



class math_block_no_params(logic_block_no_params):
    pass


class addition_block(math_block_no_params, block_with_two_inputs):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='addition_block', \
                 variable_name='add_block1', \
                 width=def_width_1, height=def_height_1, \
                 **kwargs):

        summing_junction.__init__(self, input_block1=input_block1, input_block2=input_block2, \
                                  arduino_class=arduino_class, \
                                  variable_name=variable_name, \
                                  **kwargs)
        self.width = width
        self.height = height
        if "label" in kwargs:
            label = kwargs['label']
        else:
            label = '+'
        self.label = label


    def find_output(self, i):
        output_i = self.input_block1.output_vector[i] + self.input_block2.output_vector[i]
        return self.output_vector[i]



class subtraction_block(math_block_no_params, block_with_two_inputs):
    def __init__(self, input_block1=None, input_block2=None, \
                 arduino_class='subtraction_block', \
                 variable_name='subtract_block1', \
                 width=def_width_1, height=def_height_1, \
                 **kwargs):

        summing_junction.__init__(self, input_block1=input_block1, input_block2=input_block2, \
                                  arduino_class=arduino_class, \
                                  variable_name=variable_name, \
                                  **kwargs)
        self.width = width
        self.height = height
        if "label" in kwargs:
            label = kwargs['label']
        else:
            label = '-'
        self.label = label


    def find_output(self, i):
        output_i = self.input_block1.output_vector[i] - self.input_block2.output_vector[i]
        return self.output_vector[i]


class if_block(greater_than_block):
    """Switch the output between input_block1 (true) and input_block2 (false)
    depending on the bool_input block."""
    def __init__(self, bool_input=None, input_block1=None, input_block2=None, \
                 arduino_class='if_block', \
                 variable_name='if_block1', \
                 width=def_width_1, height=3, \
                 num_inputs = 3, \
                 bool_input_name=None, \
                 gui_input_labels=['T/F Input','True Input','False Input'], \
                 set_input_func_names=['set_bool_input', \
                                       'set_input_block1', \
                                       'set_input_block2'], \
                 get_input_func_names=['get_bool_block_name', \
                                       'get_input_block1_name', \
                                       'get_input_block2_name'], \
                 param_list=['bool_input_name'], \
                 **kwargs):
        greater_than_block.__init__(self, input_block1=input_block1, input_block2=input_block2, \
                                    arduino_class=arduino_class, \
                                    variable_name=variable_name, \
                                    num_inputs=num_inputs, \
                                    gui_input_labels=gui_input_labels, \
                                    set_input_func_names=set_input_func_names, \
                                    get_input_func_names=get_input_func_names,\
                                    param_list=param_list, \
                                    **kwargs)
        self.bool_input = bool_input
        self.bool_input_name = bool_input_name
        self.width = width
        self.height = height
        if "label" in kwargs:
            label = kwargs['label']
        else:
            label = 'if'
        self.label = label
        self.yoffset = self.height*0.3


    def set_inputs(self, bool_in, in1, in2):
        self.bool_input = bool_in
        self.input_block1 = in1
        self.input_block2 = in2


    def set_bool_input(self, bool_input):
        self.bool_input = bool_input
        self.bool_input_name = self.bool_input.variable_name
        bool_input.output_block = self


    def get_bool_block_name(self):
        return self.get_attr_if_set('bool_input_name')


    def get_arduino_setup_code(self):
        # sum1.set_inputs(&u, &G);
        input_line = "%s.set_inputs(&%s, &%s, &%s);" % \
                     (self.variable_name, \
                      self.bool_input.variable_name, \
                      self.input_block1.variable_name, \
                      self.input_block2.variable_name)
        return [input_line]


    def find_output(self, i):
        if self.bool_input[i] > 0:
            output_i = self.input_block1.output_vector[i]
        else:
            output_i = self.input_block2.output_vector[i]
        return self.output_vector[i]


    def draw_input1_wire(self, ax, style='hv', **kwargs):
        self._draw_input_wire(ax, sign=1, inblock='input_block1', yoffset=0, \
                              style=style, **kwargs)


    def draw_input2_wire(self, ax, style='hv', **kwargs):
        self._draw_input_wire(ax, sign=-1, inblock='input_block2', \
                yoffset=self.yoffset, \
                style=style, **kwargs)


    def draw_bool_wire(self, ax, style='hv', **kwargs):
        self._draw_input_wire(ax, sign=1, inblock='bool_input', \
                yoffset=self.yoffset, style=style, **kwargs)


    def draw(self, ax, **kwargs):
        # - add labels for T/F, T and F wires
        # - add wire for bool block
        #def add_text(self, ax, point, text, xoffset=0, yoffset=0, \
        #         fontdict=None):
        self.place_label(ax)
        self.draw_rectangle(ax)

        # draw wires if input blocks exist:
        if self.bool_input is not None:
            self.draw_bool_wire(ax, **kwargs)

        if self.input_block1 is not None:
            self.draw_input1_wire(ax, style='vh', **kwargs)

        if self.input_block2 is not None:
            self.draw_input2_wire(ax, style='vh', **kwargs)

        le = self.left_edge
        text_x = le[0] + 0.3
        label_font = {'size': 12, 'family':'serif'}

        def mylabels(yoffset, text, ha='left'):
            self.add_text(ax, (text_x, self.y + yoffset), text, \
                          ha=ha, fontdict=label_font)

        mylabels(self.yoffset, "T/F")
        mylabels(0, "T")
        mylabels(-self.yoffset, "F")



class TF_block(block_with_one_input_setup_code):
    pass


def ndarray_to_arduino_string(array_in):
    print("array_in: %s" % array_in)
    outstr = "{"
    first = 1
    for ent in array_in:
        print("ent: %s" % ent)
        if first:
            first = 0
        else:
            outstr += ', '
        nextstr = "%0.10g" % ent
        outstr += nextstr
    outstr += '};'
    return outstr


class digcomp_block(TF_block):
    def __init__(self, Ds=None, dt=0.002, \
                 input_block1=None, \
                 label='$D(z)$', \
                 den_array=[], \
                 num_array=[],\
                 gain=1.0, \
                 variable_name='Dz_block', \
                 arduino_class='digcomp_block', \
                 param_list=['num_array','den_array','gain'], \
                 #,'a_len','b_len'], \
                 **kwargs):
        """Create a digital compensator block based on the continuous
        TF Ds if given, i.e. D(s).  Use time step dt in the c2d process, which
        probably default to tustin (see digcomp.Dig_Comp_from_ctime
        for details)."""
        TF_block.__init__(self, label=label, input_block1=input_block1, \
                          variable_name=variable_name, param_list=param_list, \
                          **kwargs)
        self.arduino_class = arduino_class
        self.Ds = Ds
        self.dt = dt

        #print("type(den_array) = %s" % type(den_array))
        #print("type(num_array) = %s" % type(num_array))

        if Ds is not None:
            self.Dz = digcomp.Dig_Comp_from_ctime(Ds, dt)
            self.num_array = self.Dz.num
            self.den_array = self.Dz.den
        else:
            if type(den_array) == str:
                den_array = parse_array_str(den_array)
            if type(num_array) == str:
                num_array = parse_array_str(num_array)

            self.num_array = num_array
            self.den_array = den_array

        self.b_len = len(self.num_array)
        self.a_len = len(self.den_array)
        self.gain = gain


    def get_python_init_code(self):
        # Ds = TF(num,den)
        clean_num = np.squeeze(self.Ds.num).tolist()
        clean_den = np.squeeze(self.Ds.den).tolist()
        line1 = "Ds = TF(%s, %s)" % (clean_num, clean_den)
        #myparamstr = self._get_python_param_str()
        myparamstr = "Ds, %0.6g" % self.dt
        #mod_str = type(self).__module__
        mod_str = "pybd"
        class_name_str = type(self).__name__
        self.python_class_str = "%s.%s" % (mod_str, class_name_str)
        pat = '%s = %s(%s)'
        line2 = pat % (self.variable_name, \
                       self.python_class_str, \
                       myparamstr)
        return [line1, line2]


    def get_python_secondary_init_code(self, Nstr="N"):
        print("Nstr = %s" % Nstr)
        line1 = "%s.init_vectors(%s)" % (self.variable_name, Nstr)
        line2 = "%s.set_input_block1(%s)" % \
                (self.variable_name, self.input_block1.variable_name)
        line3 = "%s.Dz.input = %s.output_vector" % \
                (self.variable_name, self.input_block1.variable_name)
        line4 = "%s.Dz.output = %s.output_vector" % \
                (self.variable_name, self.variable_name)
        code = [line1, line2, line3, line4]
        return code


    def find_output(self, i):
        self.output_vector[i] = int(self.Dz.calc_out(i))
        return self.output_vector[i]



    def get_arduino_init_code(self):
        #float num_array[2] = {61.57894737, -33.15789474};
        #float den_array[2] = { 1.0, -0.05263158};
        #digcomp_block Dz = digcomp_block(num_array, den_array, 2, 2, &sum1);
        #
        # Notes:
        # - I am assuming only one digcomp per system right now
        #     - not being careful about the names num_array and den_array
        # - I am not really allowing the input block to be set with the
        #   init code
        #     - it will be NULL in C and must be set later
        #
        #=====================================
        # I need to update b_len and a_len in case they have changed
        # since the block was initialized
        self.b_len = len(self.num_array)
        self.a_len = len(self.den_array)

        line1a = "float num_array_%s[%i] = " % (self.variable_name,self.b_len)
        line1b = ndarray_to_arduino_string(self.num_array)
        line1 = line1a + line1b
        line2a = "float den_array_%s[%i] = " % (self.variable_name,self.a_len)
        line2b = ndarray_to_arduino_string(self.den_array)
        line2 = line2a + line2b
        line3 = "%s %s = %s(num_array_%s, den_array_%s, %i, %i, %0.4g);" % (self.arduino_class, \
                                                         self.variable_name, \
                                                         self.arduino_class, \
                                                         self.variable_name, \
                                                         self.variable_name, \
                                                         self.b_len, \
                                                         self.a_len,
                                                         self.gain)
        return [line1, line2, line3]


class P_controller(TF_block):
    def __init__(self, Kp=1, \
                 input_block1=None, \
                 label='P', \
                 variable_name='P_block', \
                 arduino_class='P_control_block', \
                 param_list=['Kp'], default_params={'Kp':1}, \
                 py_params=['Kp'], **kwargs):
        TF_block.__init__(self, label=label, input_block1=input_block1, \
                          variable_name=variable_name, \
                          param_list=param_list, \
                          default_params=default_params, \
                          py_params=py_params, \
                          **kwargs)
        self.Kp = Kp
        self.arduino_class = arduino_class


    def _get_arduino_param_str(self, include_inputs=False):
        # example code:
        # PD_control_block PD = PD_control_block(3, 0.1, &sum1);
        pat = "%0.6g"
        params = pat % self.Kp
        if include_inputs:
            params += ", &" + self.input_block1.variable_name
        self._arduino_param_str = params
        return self._arduino_param_str


class PD_controller(TF_block):
    def __init__(self, Kp=1, Kd=0.0, \
                 input_block1=None, \
                 label='PD', \
                 variable_name='PD_block', \
                 arduino_class='PD_control_block', \
                 py_params=["Kp","Kd"], \
                 param_list=['Kp','Kd'], \
                 default_params={'Kp':1.0, 'Kd':0.0}, \
                 **kwargs):
        TF_block.__init__(self, label=label, input_block1=input_block1, \
                          variable_name=variable_name, \
                          param_list=param_list, default_params=default_params, \
                          **kwargs)
        self.Kp = Kp
        self.Kd = Kd
        self.arduino_class = arduino_class
        self.py_params = py_params


    def _get_arduino_param_str(self, include_inputs=False):
        # example code:
        # PD_control_block PD = PD_control_block(3, 0.1, &sum1);
        pat = "%0.6g, %0.6g"
        params = pat % (self.Kp, self.Kd)#, self.input_block1.variable_name)
        if include_inputs:
            params += ", &" + self.input_block1.variable_name
        self._arduino_param_str = params
        return self._arduino_param_str


    def find_output(self, i):
        # output = Kp*input + Kd*(input-prev_input)/dt
        cur_in = self.input_block1.output_vector[i]
        prev_in = self.input_block1.output_vector[i-1]
        in_dot = (cur_in-prev_in)/self.dt
        cur_out = self.Kp*cur_in + self.Kd*in_dot
        self.output_vector[i] = cur_out
        return self.output_vector[i]


class PID_controller(TF_block):
    def __init__(self, Kp=1, Kd=0.0, Ki=0.0, \
                 input_block1=None, \
                 label='PID', \
                 variable_name='PID_block', \
                 arduino_class='PID_control_block', \
                 py_params=["Kp","Kd","Ki"], \
                 param_list=['Kp','Kd','Ki'], \
                 default_params={'Kp':1.0, 'Kd':0.0, 'Ki':0.0}, \
                 **kwargs):
        TF_block.__init__(self, label=label, input_block1=input_block1, \
                          variable_name=variable_name, \
                          param_list=param_list, default_params=default_params, \
                          **kwargs)
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki
        self.arduino_class = arduino_class
        self.py_params = py_params


    def _get_arduino_param_str(self, include_inputs=False):
        # example code:
        # PD_control_block PD = PD_control_block(3, 0.1, &sum1);
        pat = "%0.6g, %0.6g, %0.6g"
        params = pat % (self.Kp, self.Kd, self.Ki)#, self.input_block1.variable_name)
        if include_inputs:
            params += ", &" + self.input_block1.variable_name
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_arduino_menu_code(self):
        #   enc.encoder_count = 0;
        line1 = "%s.initialize();" % self.variable_name
        return [line1]



class PI_controller(PID_controller):
    def __init__(self, Kp=1, Ki=0.0, \
                 input_block1=None, \
                 label='PI', \
                 variable_name='PI_block', \
                 arduino_class='PI_control_block', \
                 py_params=["Kp","Ki"], \
                 param_list=['Kp','Ki'], \
                 default_params={'Kp':1.0, 'Ki':0.0}, \
                 **kwargs):
        TF_block.__init__(self, label=label, input_block1=input_block1, \
                          variable_name=variable_name, \
                          param_list=param_list, default_params=default_params, \
                          **kwargs)
        self.Kp = Kp
        self.Ki = Ki
        self.arduino_class = arduino_class
        self.py_params = py_params


    def _get_arduino_param_str(self, include_inputs=False):
        # example code:
        # PD_control_block PD = PD_control_block(3, 0.1, &sum1);
        pat = "%0.6g, %0.6g"
        params = pat % (self.Kp, self.Ki)#, self.input_block1.variable_name)
        if include_inputs:
            params += ", &" + self.input_block1.variable_name
        self._arduino_param_str = params
        return self._arduino_param_str



class i2c_read_block(block_with_one_input_setup_code):
    """what code is needed to autogen i2c code for RTP?"""
    # ##i2c read block in feedback loop:,
    # e, cur_resp = pi.i2c_read_device(m_ino,6)#<-- question for me: what are the 6 bytes?
    # responses[i,:]= cur_resp[0:read_bytes]
    # enc_i = cur_resp[3] + cur_resp[2]*256
    # if enc_i > 30000:
    #     enc_i -= 2**16
    # enc_vect[i] = enc_i
    def __init__(self, i2c_name='', pigpio_name='pi', \
                 variable_name='i2c_block_1', \
                 pi_instance=None, i2c_connection=None, \
                 read_bytes=6, \
                 msb_index=2, lsb_index=3, \
                 label='i$^2$c', \
                 **kwargs):
        block_with_one_input_setup_code.__init__(self, variable_name=variable_name, \
                                                 label=label, **kwargs)
        self.read_bytes = read_bytes
        self.i2c_name = i2c_name
        self.pi_name = pigpio_name
        self.pi = pi_instance
        self.connection = i2c_connection
        self.msb_index = msb_index
        self.lsb_index = lsb_index
        # for init params:
        self.hardcoded_list = [("i2c_connection",self.i2c_name), \
                               ("pi_instance",self.pi_name),\
                               ]
        self.lookup_params = ["read_bytes","msb_index", "lsb_index"]


    def _get_python_param_str(self):
        """The general form of _get_python_param_str looks up
        parameter values based on a list of attr names.  For the i2c
        block, pi_instance and i2c_connection won't exist in the
        Jupyter Notebook and will need to be hardcoded based on known
        names here.  The rest of the init params can be looked up in
        the usual way.

        The pigpio connection and i2c connection must be established
        before this block is created.  The code for this is assumed to
        be in the template file, near the top."""
        # hardcoded part:
        hard_str = param_str_from_list_of_tuples(self.hardcoded_list)

        # lookup part:
        outstr = self._lookup_params_build_string(self.lookup_params)
        self._py_params = hard_str + ', ' + outstr
        return self._py_params


    def init_vectors(self, N=1000):
        self.responses = np.zeros((N,self.read_bytes))
        self.output_vector = np.zeros(N)


    def get_python_secondary_init_code(self, **kwargs):
        #line1 = "%s.init_vectors(N)" % self.variable_name
        #return [line1]
        return block.get_python_secondary_init_code(self, **kwargs)


    def read_data(self, i):
        # if I handle this like other blocks, then this code would
        # need to be run internally:
        #
        # e, cur_resp = pi.i2c_read_device(m_ino,6)#<-- question for me: what are the 6 bytes?
        # responses[i,:]= cur_resp[0:read_bytes]
        #
        # - but in order to do that, I would need the pi instance and
        #   m_ino as init parameters or something
        e, cur_resp = self.pi.i2c_read_device(self.connection,self.read_bytes)
        self.responses[i,:] = cur_resp[0:self.read_bytes]
        # now find the desired output variable from among
        # self.responses[i,:], reassembling the value from two bytes
        # (assuming a signed, two-byte int)
        value_i = cur_resp[self.lsb_index] + cur_resp[self.msb_index]*256
        if value_i > (2**15-1):
            value_i -= 2**16
        self.output_vector[i] = value_i
        return value_i


    def get_python_loop_code(self, istr='i'):
        line1 = "%s.read_data(%s)" % (self.variable_name, istr)
        return [line1]



class spi_send_block(i2c_read_block):
    # what must a valid block do?:
    # - get created
    # - generate python code
    # - have a find_output method (loop code)
    ## msb = int(v_out/256)
    ## lsb = int(v_out % 256)
    ## #senddata = [30,msb,lsb]
    ## #senddata = [17,81]
    ## spi_data = [msb, lsb, 10]

    ## time.sleep(0.0001)

    ## spi_resp = pi.spi_xfer(h_spi, spi_data)
    def __init__(self, spi_name='', pigpio_name='pi', \
                variable_name='spi_block_1', \
                pi_instance=None, spi_connection=None, \
                label='spi', \
                **kwargs):
        block_with_one_input_setup_code.__init__(self, variable_name=variable_name, \
                                                 label=label, **kwargs)
        self.spi_name = spi_name
        self.pi_name = pigpio_name
        self.pi = pi_instance
        self.spi_connection = spi_connection
        # for init params:
        self.hardcoded_list = [("spi_connection",self.spi_name), \
                               ("pi_instance",self.pi_name),\
                               ]
        self.lookup_params = []


    def get_python_loop_code(self, istr='i'):
        line1 = "%s.send_data(%s)" % (self.variable_name, istr)
        return [line1]


    def send_data(self, i):
        """For the spi send block, this is loop code that doesn't
        really determine an output.  spi_send_block's don't really
        have outputs."""
        cur_input = self.input_block1.output_vector[i]
        if cur_input < 0:
            cur_input += 2**16

        msb = int(cur_input/256)
        lsb = int(cur_input % 256)
        spi_data = [msb, lsb, 10]
        self.pi.spi_xfer(self.spi_connection, spi_data)
        self.msb_vect[i] = msb
        self.lsb_vect[i] = lsb
        # fake output
        return 0


    def init_vectors(self, N=1000):
        self.msb_vect = np.zeros(N)
        self.lsb_vect = np.zeros(N)
        self.output_vector = np.zeros(N)


    def get_python_secondary_init_code(self, **kwargs):
        return block_with_one_input_setup_code.get_python_secondary_init_code(self, **kwargs)


class plant(TF_block):
    def __init__(self, sensor=None, actuator=None, label="$G(s)$", \
                 input_block1=None,\
                 variable_name='G_block', \
                 arduino_class='plant', \
                 width=3, height=2, \
                 fontdict = {'size': 20, 'family':'serif'}, \
                 param_list=['actuator_name','sensor_name'],\
                 **kwargs):
        TF_block.__init__(self, label=label, input_block1=input_block1, variable_name=variable_name, \
                          width=width, height=height, fontdict=fontdict, \
                          param_list=param_list, **kwargs)
        self.sensor = sensor
        self.actuator = actuator
        self.arduino_class = arduino_class
        # handle this better:
        if 'actuator_name' in kwargs:
            self.actuator_name = kwargs['actuator_name']
        else:
            if self.actuator is not None:
                self.actuator_name = self.actuator.variable_name

        if 'sensor_name' in kwargs:
            self.sensor_name = kwargs['sensor_name']
        else:
            if self.sensor is not None:
                self.sensor_name = self.sensor.variable_name


    def replace_actuator(self, new_inst):
        # leaving it up to the block_diagram system to deleter the old instance
        # - see block_diagram.replace_actuator
        self.actuator = new_inst
        self.actuator_name = new_inst.variable_name


    def replace_sensor(self, new_inst):
        # leaving it up to the block_diagram system to deleter the old instance
        # - see block_diagram.replace_sensor
        self.sensor = new_inst
        self.sensor_name = new_inst.variable_name



    def _set_sensor_x_and_y(self):
        print("self.x = %0.4g" % self.x)
        print("self.width = %0.4g" % self.width)
        self.sensor.x = self.x + 0.5*self.width
        self.sensor.y = self.y
        self.sensor.width = 0
        self.sensor.height = 0


    def place_absolute(self, *args, **kwargs):
        TF_block.place_absolute(self, *args, **kwargs)
        self._set_sensor_x_and_y()


    def place_relative(self, *args, **kwargs):
        TF_block.place_relative(self, *args, **kwargs)
        self._set_sensor_x_and_y()


    def _get_arduino_param_str(self):
        # plant G = plant(&HB, &enc);
        params = "&%s, &%s" % (self.actuator.variable_name, self.sensor.variable_name)
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_code_one_section(self, method_name="get_arduino_init_code"):
        """Call the method method_name on parent class, actuator, and
        sensor and return the three lists concatenated"""
        parent_method = getattr(block_with_one_input_setup_code, method_name)
        mylist = parent_method(self)
        act_method = getattr(self.actuator, method_name)
        sensor_method = getattr(self.sensor, method_name)
        act_list = act_method()
        sensor_list = sensor_method()
        return act_list + sensor_list + mylist


    ## def get_arduino_init_code(self):
    ##     act_init = self.actuator.get_arduino_init_code()
    ##     sense_init = self.sensor.get_arduino_init_code()
    ##     my_init = TF_block.get_arduino_init_code(self)
    ##     return act_init + sense_init + my_init

    def get_arduino_init_code(self):
        full_list = self.get_code_one_section("get_arduino_init_code")
        return full_list


    ## def get_arduino_setup_code(self):
    ##     mylist = block_with_one_input_setup_code.get_arduino_setup_code(self)
    ##     act_list = self.actuator.get_arduino_setup_code()
    ##     sense_list = self.sensor.get_arduino_setup_code()
    ##     return act_list + sense_list + mylist


    def get_arduino_setup_code(self):
        full_list = self.get_code_one_section("get_arduino_setup_code")
        return full_list


    def get_arduino_menu_code(self):
        full_list = self.get_code_one_section("get_arduino_menu_code")
        return full_list


    def get_arduino_menu2_code(self):
        full_list = self.get_code_one_section("get_arduino_menu2_code")
        return full_list



    def get_arduino_menu3_code(self):
        full_list = self.get_code_one_section("get_arduino_menu3_code")
        return full_list



    def get_arduino_loop_code(self):
        """Code to be executed in the Arduino loop method for the block"""
        # assumed form:
        # u.find_output(t_sec);
        pat = '%s.find_output(t_sec);'
        line1 = pat % self.variable_name
        return [line1]


    def get_arduino_secondary_loop_code(self):
        line1 = "%s.send_command();" % (self.variable_name)
        return [line1]


class i2c_plant(plant):
    def __init__(self, sensor=None, actuator=None,
                 input_block1=None,\
                 arduino_class='i2c_plant', \
                 #width=3, height=2, \
                 #fontdict = {'size': 20, 'family':'serif'}, \
                 #param_list=['actuator_name','sensor_name'],\
                 **kwargs):
        # label="$G(s)$", \
        # variable_name='G_block', \
        plant.__init__(self, sensor=sensor, \
                        actuator=actuator, \
                        input_block1=input_block1, \
                        arduino_class=arduino_class, **kwargs)
        #TF_block.__init__(self, label=label, input_block1=input_block1, variable_name=variable_name, \
        #                  width=width, height=height, fontdict=fontdict, \
        #                  param_list=param_list, **kwargs)


    def get_arduino_setup_code(self, fd_str="uno_fd"):
        base_list = block_with_one_input_setup_code.get_arduino_setup_code(self)

        line1 = "%s.set_act_fd(%s);" % (self.variable_name,fd_str)
        line2 = "%s.set_sensor_fd(%s);" % (self.variable_name,fd_str)
        return base_list + [line1, line2]


    def get_rpi_secondary_loop_code(self, istr='i'):
        line1 = "%s.send_command(%s);" % (self.variable_name, istr)
        return [line1]


    def get_arduino_secondary_loop_code(self, istr='i'):
        line1 = "%s.send_command(%s);" % (self.variable_name, istr)
        return [line1]


    def get_rpi_end_test_code(self):
        line1 = "%s.stop();" % (self.variable_name)
        return [line1]


    def get_rpi_start_test_code(self):
        line1 = "%s.start_test();" % (self.variable_name)
        return [line1]




class plant_no_actuator(plant):
    def __init__(self, sensor=None, label="$G(s)$", \
                 input_block1=None,\
                 variable_name='G_block', \
                 arduino_class='plant_no_actuator', \
                 width=3, height=2, \
                 fontdict = {'size': 20, 'family':'serif'}, \
                 param_list=['sensor_name'], \
                 py_params=['sensor_name'], \
                 **kwargs):
        print("in plant_no_actuator.__init__, kwargs:")
        print(kwargs)
        # Why do I call TF_block.__init__ instead of plant.__init__ here?:
        # - maybe because I want no actuator?
        # - there are other things I do at the end of plant.__init__ that
        #   I probably want here, such as handling sensor_name when loading and
        #   sensor is still None
        TF_block.__init__(self, label=label, input_block1=input_block1, variable_name=variable_name, \
                          width=width, height=height, fontdict=fontdict, param_list=param_list, \
                          py_params=py_params, \
                          **kwargs)
        self.sensor = sensor
        self.arduino_class = arduino_class
        if self.sensor is not None:
            self.sensor_name = self.sensor.variable_name
        else:
            if 'sensor_name' in kwargs:
                self.sensor_name = kwargs['sensor_name']
            else:
                self.sensor_name = ""


    def _get_arduino_param_str(self):
        # plant G = plant(&myaccel);
        params = "&%s" % self.sensor.variable_name
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_code_one_section(self, method_name="get_arduino_init_code"):
        """Call the method method_name on parent class, actuator, and
        sensor and return the three lists concatenated"""
        parent_method = getattr(block_with_one_input_setup_code, method_name)
        mylist = parent_method(self)
        sensor_method = getattr(self.sensor, method_name)
        sensor_list = sensor_method()
        return sensor_list + mylist


    def get_arduino_loop_code(self):
        # do not need to send a command, unlike other plants that have actuators
        other_lines = block_with_one_input_setup_code.get_arduino_loop_code(self)
        # assume no actuator or sensor actions in the loop
        return other_lines


class plant_with_double_actuator(block_with_two_inputs, plant):
    def __init__(self, sensor=None, actuator=None, label="$G(s)$", \
                 input_block1=None, input_block2=None, \
                 arduino_class='plant_with_double_actuator', \
                 variable_name='G_block', \
                 width=3, \
                 height=2, \
                 py_params=[], \
                 param_list=['sensor_name','actuator_name'],\
                 **kwargs):
        block_with_two_inputs.__init__(self,label=label, arduino_class=arduino_class, \
                                       variable_name=variable_name, \
                                       width=width, height=height, \
                                       param_list=param_list, **kwargs)
        self.sensor = sensor
        self.actuator = actuator
        self.input_block1 = input_block1
        self.input_block2 = input_block2
        self.py_params = py_params

        if 'actuator_name' in kwargs:
            self.actuator_name = kwargs['actuator_name']
        else:
            if self.actuator is not None:
                self.actuator_name = self.actuator.variable_name

        if 'sensor_name' in kwargs:
            self.sensor_name = kwargs['sensor_name']
        else:
            if self.sensor is not None:
                self.sensor_name = self.sensor.variable_name



    # what needs to be different here?
    # - two inputs
    def get_arduino_setup_code(self):
        # G.set_input(&Dz);
        input_block_line = "%s.set_input_blocks(&%s, &%s);" % (self.variable_name, \
                                                               self.input_block1.variable_name, \
                                                               self.input_block2.variable_name)
        sensor_list = self.sensor.get_arduino_setup_code()
        act_list = self.actuator.get_arduino_setup_code()
        return sensor_list + act_list + [input_block_line]


    def get_arduino_loop_code(self):
        #send_command
        #line1 = "%s.send_commands();" % self.variable_name
        other_lines = block_with_one_input_setup_code.get_arduino_loop_code(self)
        # assume no actuator or sensor actions in the loop
        #return [line1] + other_lines
        return other_lines


    def get_arduino_secondary_loop_code(self):
        line1 = "%s.send_commands();" % (self.variable_name)
        return [line1]


class plant_with_double_actuator_two_sensors(plant_with_double_actuator):
    """This class represents a system like the cart/pendulum robot
    that has a dual motor actuator and two sensors (the line sensor
    and the pendulum encoder).  Each sensor needs to behave like a
    block as far as other blocks are concerned.  For example, they
    should have find_output and get_output methods.

    My intention is to have the sensors have wire outputs near the top
    and bottom of the right edge of the plant.  Blocks that have the
    sensors as their inputs need to be able to draw wires from the
    sensor connections.  So, the sensors will need to have x and y
    coordinates that get set when the plant block is placed.  My wire
    guessing code was based around the accidental assumption that the
    x,y coordinates refer to the center of a block.  I can probably
    work around this by setting the sensors to have zero height and/or
    zero width.


    What needs to happen in the loop, init code, setup code, etc. for
    this block to do what it needs to do?

    Note: this block has no py_params, nor any default_params and as
    such is not ready for python usage."""
    def __init__(self, sensor1, sensor2, actuator, label="$G(s)$", \
                 input_block1=None, input_block2=None, \
                 arduino_class='plant_with_double_actuator_two_sensors', \
                 variable_name='G_block', \
                 width=3, \
                 height=2, \
                 py_params=[], \
                 param_list=['sensor1_name','sensor2_name','actuator_name'],\
                 **kwargs):
        block_with_two_inputs.__init__(self,label=label, arduino_class=arduino_class, \
                                       variable_name=variable_name, \
                                       width=width, height=height, \
                                       param_list=param_list, \
                                       **kwargs)
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.actuator = actuator
        self.actuator_name = actuator.variable_name
        self.sensor1_name = sensor1.variable_name
        self.sensor2_name = sensor2.variable_name
        self.input_block1 = input_block1
        self.input_block2 = input_block2
        self.py_params = py_params


    def _get_arduino_param_str(self):
        # plant G = plant(&HB, &enc);
        params = "&%s, &%s, &%s" % (self.actuator.variable_name, \
                                   self.sensor1.variable_name, \
                                   self.sensor2.variable_name)
        self._arduino_param_str = params
        return self._arduino_param_str



    def get_code_one_section(self, method_name="get_arduino_init_code"):
        """Call the method method_name on parent class, actuator, and
        sensor and return the three lists concatenated"""
        parent_method = getattr(block_with_one_input_setup_code, method_name)
        mylist = parent_method(self)
        act_method = getattr(self.actuator, method_name)
        act_list = act_method()
        sensor1_method = getattr(self.sensor1, method_name)
        sensor1_list = sensor1_method()
        sensor2_method = getattr(self.sensor2, method_name)
        sensor2_list = sensor2_method()
        return act_list + sensor1_list + sensor2_list + mylist


    def _set_sensors_x_and_y(self):
        print("self.x = %0.4g" % self.x)
        print("self.width = %0.4g" % self.width)
        self.sensor1.x = self.x + 0.5*self.width
        self.sensor2.x = self.x + 0.5*self.width
        self.sensor1.y = self.y + 0.4*self.height
        self.sensor2.y = self.y - 0.4*self.height
        self.sensor1.width = 0
        self.sensor1.height = 0
        self.sensor2.width = 0
        self.sensor2.height = 0


    def place_absolute(self, *args, **kwargs):
        block_with_two_inputs.place_absolute(self, *args, **kwargs)
        # - are outputs hardwired to the right?
        #     - that is a labview convention
        # - are inputs hardwired to the left?
        self._set_sensors_x_and_y()



    def place_relative(self, *args, **kwargs):
        block_with_two_inputs.place_relative(self, *args, **kwargs)
        self._set_sensors_x_and_y()


class plant_with_two_i2c_inputs_and_two_i2c_sensors(plant_with_double_actuator_two_sensors):
    def __init__(self, sensor1=None, sensor2=None, send_address=7, \
                 read_address1=7, read_address2=8, i2c=None, \
                 variable_name="G", \
                 sensor1_name = None, sensor2_name = None, \
                 py_params=['sensor1_name','sensor2_name','send_address', 'read_address1', \
                            'read_address2'], \
                 default_params = {'read_address1':7, 'read_address2':8, 'send_address':7}, \
                 **kwargs):
        print("in plant_with_two_i2c_inputs_and_two_i2c_sensors __init__, kwargs:")
        print(kwargs)
        block_with_two_inputs.__init__(self, variable_name=variable_name, \
                                       py_params=py_params, \
                                       default_params=default_params, \
                                       **kwargs)
        if self.label is None:
            self.label = variable_name
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        # need to set sensor1_name and sensor2_name
        if sensor1 is not None:
            self.sensor1_name = sensor1.variable_name
        else:
            self.sensor1_name = sensor1_name
        if sensor2 is not None:
            self.sensor2_name = sensor2.variable_name
        else:
            self.sensor2_name = sensor2_name
        self.i2c = i2c
        self.variable_name = variable_name
        self.send_address = send_address
        self.read_address1 = read_address1
        self.read_address2 = read_address2
        self.read1_bytyes = 8


    def _get_python_param_str(self):
        lookup_params = ['send_address', 'read_address1', 'read_address2']
        start = "sensor1=%s, sensor2=%s, " % \
                (self.sensor1.variable_name, self.sensor2.variable_name)
        middle = self._lookup_params_build_string(lookup_params)
        end = " ,i2c=i2c"
        outstr = start+middle+end
        self._py_params = outstr
        return outstr


    def get_python_loop_code(self, istr='i'):
        """Get the code that will be called inside the main loop in
        the python experimental file.  For many blocks, this will just be
        myname.find_output(i)

        Keep in mind that this means that all blocks need to have a
        find_output method.

        It might make sense to move this to the block class at a later
        time.  A sensor or actuator might have their loop code called
        the plant object."""
        line1 = "%s.find_output(%s)" % (self.variable_name, istr)
        return [line1]


    def get_python_secondary_loop_code(self, istr='i'):
        line1 = "%s.send_commands(%s)" % (self.variable_name, istr)
        return [line1]



class cart_pendulum(plant_with_two_i2c_inputs_and_two_i2c_sensors):
    def __init__(self, label="$G_{cart}$", \
                 sensor1=None, sensor2=None, \
                 input_block1=None, input_block2=None, \
                 sensor1_name = None, sensor2_name = None, \
                 send_address=7, \
                 arduino_class='plant_with_i2c_double_actuator_and_two_sensors', \
                 variable_name='G_cart', \
                 input_block1_name=None, \
                 input_block2_name=None, \
                 width=3, \
                 height=2, \
                 py_params=[], \
                 param_list=['sensor1_name','sensor2_name','send_address'], \
                 **kwargs):
        block_with_two_inputs.__init__(self, label=label, \
                                        input_block1=input_block1, \
                                        input_block2=input_block2, \
                                        input_block1_name=input_block1_name, \
                                        input_block2_name=input_block2_name, \
                                        arduino_class=arduino_class, \
                                        variable_name=variable_name, \
                                        param_list=param_list, \
                                        py_params=py_params, \
                                        **kwargs)
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        # need to set sensor1_name and sensor2_name
        if sensor1 is not None:
            self.sensor1_name = sensor1.variable_name
        else:
            self.sensor1_name = sensor1_name
        if sensor2 is not None:
            self.sensor2_name = sensor2.variable_name
        else:
            self.sensor2_name = sensor2_name

        self.send_address = send_address


    def _get_arduino_param_str(self):
        # plant G = plant(&HB, &enc);
        params = "%i, &%s, &%s" % (self.send_address, \
                                   self.sensor1.variable_name, \
                                   self.sensor2.variable_name)
        self._arduino_param_str = params
        return self._arduino_param_str



    def get_arduino_init_code(self):
        """Code to be executed to create an instance of the block in
        Arduino code"""
        # specific example:
        #
        # step_input u = step_input(0.5, 150);
        #
        # assumed pattern:
        #
        # arduino_class variable_name = arduino_class(param_str)
        #sensor1_method = getattr(self.sensor1, method_name)
        sensor1_list = self.sensor1.get_arduino_init_code()
        sensor2_list = self.sensor2.get_arduino_init_code()

        #sensor2_method = getattr(self.sensor2, method_name)
        #sensor2_list = sensor2_method()
        self._get_arduino_param_str()
        pat = '%s %s = %s(%s);'
        line1 = pat % (self.arduino_class, \
                       self.variable_name, \
                       self.arduino_class, \
                       self._arduino_param_str)
        return sensor1_list + sensor2_list + [line1]


    def get_arduino_loop_code(self):
        #send_command
        line1 = "%s.find_output();" % self.variable_name
        #other_lines = block_with_one_input_setup_code.get_arduino_loop_code(self)
        # assume no actuator or sensor actions in the loop
        return [line1]#+ other_lines



    def get_arduino_menu_code(self):
        # probably not common, so let it be ok not to override:
        return []


    def get_arduino_secondary_loop_code(self):
        """Probably not needed for most blocks, but required for
        some plants that need to send commands at the end of the loop"""
        line1 = "%s.send_commands(nISR);" % self.variable_name
        return [line1]


    def get_rpi_secondary_loop_code(self):
        """Probably not needed for most blocks, but required for
        some plants that need to send commands at the end of the loop"""
        line1 = "%s.send_commands(i);" % self.variable_name
        return [line1]


    def get_arduino_print_code(self):
        # Assuming int output for now
        # - print_comma_then_int(G.read_output());
        print_line = "print_comma_then_int(%s.read_output());" % self.variable_name
        return [print_line]


    def get_code_one_section(self, method_name="get_arduino_init_code"):
        """What does this class need to do for teensyduino cart pendulum control?
        - I believe the underlying Arduino code handles calling the sensor methods when needed
        - I also need secondary loop code for sending the commands over i2c
        - what are the methods that generate the part of the Arduino code and
          can they be inherited from parent classes?
          - or do they need to be overridden?
          - see arduino_code_gen_object's methods
        """
        #parent_method = getattr(block_with_one_input_setup_code, method_name)
        #mylist = parent_method(self)
        #act_method = getattr(self.actuator, method_name)
        #act_list = act_method()
        #sensor1_method = getattr(self.sensor1, method_name)
        #sensor1_list = sensor1_method()
        #sensor2_method = getattr(self.sensor2, method_name)
        #sensor2_list = sensor2_method()
        #return act_list + sensor1_list + sensor2_list + mylist
        #
        # This might set up an infinite loop:
        print("in get_code_one_section, method_name = %s" % method_name)
        my_method = getattr(self, method_name)
        mylist = my_method()
        return mylist


class cart_pendulum_v2(cart_pendulum):
    def __init__(self, label="$G_{cartv2}$", \
                 sensor1=None, sensor2=None, \
                 input_block1=None, input_block2=None, \
                 sensor1_name = None, sensor2_name = None, \
                 send_address=7, \
                 arduino_class='plant_with_rpi_motor_hat', \
                 variable_name='G_cartv2', \
                 input_block1_name=None, \
                 input_block2_name=None, \
                 width=3, \
                 height=2, \
                 py_params=[], \
                 param_list=['sensor1_name','sensor2_name'], \
                 **kwargs):
        block_with_two_inputs.__init__(self, label=label, \
                                        input_block1=input_block1, \
                                        input_block2=input_block2, \
                                        input_block1_name=input_block1_name, \
                                        input_block2_name=input_block2_name, \
                                        arduino_class=arduino_class, \
                                        variable_name=variable_name, \
                                        param_list=param_list, \
                                        py_params=py_params, \
                                        **kwargs)
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        # need to set sensor1_name and sensor2_name
        if sensor1 is not None:
            self.sensor1_name = sensor1.variable_name
        else:
            self.sensor1_name = sensor1_name
        if sensor2 is not None:
            self.sensor2_name = sensor2.variable_name
        else:
            self.sensor2_name = sensor2_name

        self.send_address = send_address


    def _get_arduino_param_str(self):
        # plant G = plant(&HB, &enc);
        params = "&%s, &%s" % (self.sensor1.variable_name, \
                               self.sensor2.variable_name)
        self._arduino_param_str = params
        return self._arduino_param_str


    def get_arduino_setup_code(self):
        inherited_code = cart_pendulum.get_arduino_setup_code(self)
        #input_block_line = "%s.set_input_blocks(&%s, &%s);" % (self.variable_name, \

        pin_line = "%s.init_pins();" % self.variable_name
        outlines = inherited_code + [pin_line]
        return outlines


class plot_code_generator(object):
    """A class for specifying a matplotlib plot whose code will be
    auto-generated as part of a block_diagram system's plotting code."""
    def __init__(self, item_list, fignum=None, \
                 x_var='t', xlim=None, ylim=None, \
                 xlabel=None, ylabel="Signal Amp. (counts)", \
                 legend=None, legloc=None, \
                 title=None):
        self.item_list = item_list
        self.fignum = fignum
        self.x_var = x_var
        self.xlabel = xlabel
        self.xlim = xlim
        self.ylabel = ylabel
        self.ylim = ylim
        self.legloc = legloc
        self.legend = legend
        self.title = title

        # guess some optional inputs
        if xlabel is None:
            if x_var == 't':
                self.xlabel = "Time (sec.)"

        if legend is None:
            if type(item_list[0]) == str:
                self.legend = item_list


    def get_python_code(self):
        code = []
        out = code.append
        if self.fignum is None:
            out("plt.figure()")
        else:
            out("plt.figure(%i)" % self.fignum)

        plot_str = ""
        for item in self.item_list:
            if plot_str:
                plot_str += ', '
            plot_str += '%s, ' % self.x_var
            if type(item) == str:
                plot_str += item
            elif isinstance(item, block):
                outstr = "%s.output_vector" % item.variable_name
                plot_str += outstr
        plot_line = "plt.plot(%s)" % plot_str
        code.append(plot_line)

        lookup_strs = ['xlabel','ylabel','title']
        lookup_lists = ['xlim','ylim']
        lookup_attrs = lookup_lists + lookup_strs

        for attr in lookup_attrs:
            val = getattr(self, attr)
            if val is not None:
                # plt.xlim(self.xlim)
                if attr in lookup_strs:
                    line = 'plt.%s("%s")' % (attr, val)
                else:
                    line = "plt.%s(%s)" % (attr, val)
                out(line)

        if self.legend is not None:
            legstr = "plt.legend(%s" % self.legend
            if self.legloc is not None:
                legstr += ", loc=%s" % self.legloc
            legstr += ")"
            out(legstr)

        code.append('')
        return code


def find_next_name(base_name, name_list):
    """If a block_diagram has only one sensor, or actuator, or
    whatever, I don't want to number it.  Otherwise, append a number
    until we get to a new name."""
    if base_name not in name_list:
        return base_name
    else:
        for i in range(2,100):
            outname = base_name + str(i)
            if outname not in name_list:
                return outname


def find_name_from_suggestion(class_name, mysuggestions, list_to_check):
    if class_name not in mysuggestions:
        return "no_suggestion"
    else:
        basename = mysuggestions[class_name]
        if not basename:
            return ""
        else:
            return find_next_name(basename, list_to_check)


def check_for_inputs_in_block_list(block, block_list, sensor_list=[],  \
                                   other_blocks=[], other_sensors=[], debug=0):
    """As part of sorting blocks for execution order, I need to know
    if the inputs to a block are already in the list of blocks whose
    execution order has been identified.  If the input(s) to block are
    already in block_list, then it is ok to append block to the list.

    other_blocks and other_sensors allow for passing in blocks or
    sensors from lower numbered loops that have already been sorted
    into a valid exec_order."""
    # Assumption: block must have self.input_block1 set; all blocks
    # whose classes are known to have no inputs should already be in list
    msg = "you cannot find the execution order for blocks whose inputs are not set: %s" % block
    assert block.input_block1 is not None, msg

    if debug:
        print("block: %s" % block.variable_name)
        print("blocks already in list:")
        print_block_names(block_list)

    # possible cases:
    # - block has only 1 input
    #     - if it is in block_list, return True
    #     - if it is not in block_list, return False
    # - block has two inputs
    #     - if they are both in block_list, return True
    #     - othewise return False

    bool1 = False
    bool2 = False
    bool3 = False

    full_block_list = block_list + other_blocks
    full_sensor_list = sensor_list + other_sensors

    if block.input_block1 in full_block_list:
        bool1 = True
    elif block.input_block1 in full_sensor_list:
        bool1 = True

    if hasattr(block, "input_block2"):
        if block.input_block2 in full_block_list:
            bool2 = True
        elif block.input_block2 in full_sensor_list:
            bool2 = True
    else:
        # if the block does not have an input_block2, then this is
        # True
        bool2 = True

    if hasattr(block, "bool_input"):
        if block.bool_input in full_block_list:
            bool3 = True
        elif block.bool_input in full_sensor_list:
            bool3 = True
    else:
        bool3 = True
    # have we handled all cases?
    # - if input_block1 was not in block_list, we would have kicked out
    # - if input_block2 is defined and not in block_list, we would have kicked out
    # - if neiter of those things happened, I think we are ok


    out_bool = bool1 and bool2 and bool3
    return out_bool


def print_block_names(block_list):
    for curblock in block_list:
        print(curblock.variable_name)


def print_list(mylist):
    for item in mylist:
        print(item)



class block_diagram(object):
    def __init__(self, block_name_list=[], block_dict={}, block_list=[], axis=None, \
                 dt=0.004, \
                 welcome_msg="auto-generated Arduino code", \
                 fontdict={'size': 16, 'family':'serif'}, \
                 actuators_dict={}, \
                 actuator_name_list=[], \
                 sensors_dict={}, \
                 sensor_name_list=[], \
                 max_loops=3, \
                 ):
        self.block_name_list = block_name_list
        self.block_dict = block_dict
        self.block_list = block_list
        self.ax = axis
        self.welcome_msg = welcome_msg
        self.plot_list = []
        self.dt = dt
        self.output_variables = []
        self.fontdict = fontdict
        self.actuators_dict = actuators_dict
        self.actuator_name_list = actuator_name_list
        self.sensors_dict = sensors_dict
        self.sensor_name_list = sensor_name_list
        self.max_loops = max_loops


    def replace_block(self, old_block, new_block):
        """Replace old_block with new_block everywhere in the model:
           - as an input to other blocks
           - as a relative placement reference
           - also replace in the block_diagram block_dict, block_name_list, and
             block_list
             - and anywhere else it might appear
        """
        print("at the start of replace_block, block_dict: ")
        print(self.block_dict)
        old_block_name = old_block.variable_name
        new_block_name = new_block.variable_name
        #self.block_name_list.remove(old_block_name)
        #self.block_dict.pop(old_block_name)
        self.append_block(new_block)


        attr_dict = {'input_block1_name':'input_block1', \
                     'input_block2_name':'input_block2', \
                     }

        block_list = self.get_block_list()

        for curblock in block_list:
            for attr, other_attr in attr_dict.items():
                if hasattr(curblock, attr):
                    value = getattr(curblock, attr)
                    if value == old_block_name:
                        # set the input block instance and the input block
                        # name both to None
                        setattr(curblock, attr, new_block_name)
                        setattr(curblock, other_attr, new_block)
                        #curblock.unplace_block()

        # handle relative placement
        for curblock in block_list:
            if hasattr(curblock, "rel_block_name"):
                if curblock.rel_block_name == old_block_name:
                    curblock.rel_block_name = new_block.variable_name
                    curblock.rel_block = new_block


        # need to handle print blocks
        if hasattr(self, 'print_blocks'):
            if old_block in self.print_blocks:
                ind = self.print_blocks.index(old_block)
                self.print_blocks[ind] = new_block

        self.delete_block(old_block)
        print("at the end of replace_block, block_dict: ")
        print(self.block_dict)


    def append_actuator(self, actuator):
        """Append actuator to self.actuators and self.actuators_dict.  Assume that
        actuator has a variable_name param that is the key for the dict."""
        act_name = actuator.variable_name
        assert act_name, "actuator name cannot be empty or None: %s" % actuator
        assert act_name not in self.actuators_dict, "already have actuator by that name: %s" % act_name
        self.actuators_dict[act_name] = actuator
        self.actuator_name_list.append(act_name)


    def replace_actuator(self, old_name, new_name, new_instance):
        # I need to replace the actuator in the plant instance
        # and in the block_diagram system
        old_inst = self.actuators_dict.pop(old_name)
        old_ind = self.actuator_name_list.index(old_name)
        self.actuator_name_list.pop(old_ind)
        del old_inst
        self.append_actuator(new_instance)



    def append_sensor(self, sensor):
        """Append sensor to self.sensors and self.sensors_dict.  Assume that
        sensor has a variable_name param that is the key for the dict."""
        sensor_name = sensor.variable_name
        assert sensor_name, "sensor name cannot be empty or None: %s" % sensor
        assert sensor_name not in self.sensors_dict, "already have sensor by that name: %s" % sensor_name
        self.sensors_dict[sensor_name] = sensor
        self.sensor_name_list.append(sensor_name)


    def replace_sensor(self, old_name, new_name, new_instance):
        # I need to replace the actuator in the plant instance
        # and in the block_diagram system
        old_inst = self.sensors_dict.pop(old_name)
        old_ind = self.sensor_name_list.index(old_name)
        self.sensor_name_list.pop(old_ind)
        del old_inst
        self.append_sensor(new_instance)


    def suggest_actuator_name(self, actuator_class_name):
        #actuator_list = ['h_bridge', 'custom_actuator', 'pwm_output']#from running findallsubclasses in jupyter
        mysuggestions = {"h_bridge":'h_bridge_act', \
                         "pwm_output":'pwm_out_act', \
                         "custom_actuator":"", \
                         "i2c_actuator":"i2c_act", \
                         }
        return find_name_from_suggestion(actuator_class_name, mysuggestions, self.actuator_name_list)


    def suggest_sensor_name(self, sensor_class_name):
        #sensor_list = ['encoder', 'analog_input', 'custom_sensor']
        mysuggestions = {"encoder":'encoder_sensor', \
                         "analog_input":'analog_in_sensor', \
                         "custom_sensor":"", \
                         "accelerometer":"myaccel", \
                         "i2c_sensor":"i2c_sens", \
                         }
        return find_name_from_suggestion(sensor_class_name, mysuggestions, self.sensor_name_list)


    def suggest_block_name(self, block_type):
        """block_type is a string referring to the class of the block.
        Based on this class, follow a set of rules to pick a base
        name.  If the base name is already in self.block_name_list,
        keep increasing an appended integer until the name is
        new/unique."""
        mypairs = [("plant",'G'), ("controller",'D'), ("addition", "add"), \
                   ("subtract", "subtract"), ("input","U"), ("output","Y"), \
                   ("int_constant_block","Uconst"), \
                   ("float_constant_block","Ufloat"), \
                   ("greater_than","gt_block"),("less_than","lt_block"), \
                   ("summing_junction","sum_junct"), \
                   ("saturation_block", "sat"), \
                   ("sat2_adjustable_block", "adj_sat"), \
                   ("cart_pendulum", 'G_cart'), \
                   ("if_block","if_then"), \
                   ("output_block","Y"), \
                   ("and_block","andBlock"), \
                   ("or_block","orBlock"), \
                   ("less_than_block","lt_block"), \
                   ("switch_block","switchBlock"), \
                   ("abs_block","absBlock"), \
                   ("sloped_step","U_sloped"), \
                   ("prev_hold_block","prev_hold"), \
                   ("loop_count_block","loop_count"), \
                   ("digcomp","Dz"), \
                   ]
        if isinstance(block_type, block):
            block_type = type(block_type).__name__
        found = 0
        for key, name in mypairs:
            if key in block_type:
                base_name = name
                found = 1
                break

        if found == 0:
            return ""
        else:
            if base_name not in self.block_name_list:
                return base_name
            else:
                for i in range(2,100):
                    outname = base_name + str(i)
                    if outname not in self.block_name_list:
                        return outname
            return ""


        #self.block_name_list


    def append_block_to_dict(self, block_name, block):
        assert block_name not in self.block_dict, "block with that name already exists"
        self.block_dict[block_name] = block
        if not block.variable_name:
            block.variable_name = block_name
        self.block_name_list.append(block_name)



    def append_block(self, block):
        """Append a block to self.block_dict using block.variable_name
        as the block name.  Calls self.append_block_to_dict."""
        #assert block.variable_name, \
        #       "A block must have a variable name to be appended to self.block_dict"
        if not block.variable_name:
            block_name = self.suggest_block_name(block)
            self.append_block_to_dict(block_name, block)
        else:
            self.append_block_to_dict(block.variable_name, block)


    def guess_block_placement(self, block_name, block):
        ## How should this work?
        ##
        ## - am I the first block?
        ##     - place absolutely at (0,0)
        ## - do I have an input?
        ##     - place me to the right of my input
        ## - default to putting me to the right of the right-most block

        ## Can I assume I am already in block_name_list and block_dict?
        ## - is there harm in calling append_block_to_dict if
        ##   I am not in there already?
        if block_name not in self.block_dict:
            self.append_block_to_dict(block_name, block)

        success = 0
        if len(self.block_name_list) == 1:
            #I am the first block
            block.place_absolute(0,0)
            success = 1
        elif block.input_block1_name:
            #I have a specified input, go to the right of it
            block.place_relative(rel_block=block.input_block1)
            success = 1
        else:
            ## place to the right of the most recent block
            prev_block_name = self.block_name_list[-2]
            prev_block = self.get_block_by_name(prev_block_name)
            block.place_relative(rel_block=prev_block)
            success = 1

        return success



    def change_block_name(self, block, new_name, old_name):
        """Change the name associated with the block instance from
        old_name to new_name.  The variable name for the block needs
        to be changed as well as any references to that block from
        other blocks, such as if it is an input to another block."""
        block.variable_name = new_name
        print("in change_block_name, old_name: %s, new_name: %s")

        # to do:
        # - what about relative placement references?

        # iterate over all blocks checking for old_name
        block_list = self.get_block_list()
        attr_dict = {'input_block1_name':'set_input_block1', \
                     'input_block2_name':'set_input_block2', \
                     'rel_block_name':'change_rel_block_name', \
                     }


        for curblock in block_list:
            for attr, func_name in attr_dict.items():
                if hasattr(curblock, attr):
                    value = getattr(curblock, attr)
                    if value == old_name:
                        print("found match: %s" % curblock)
                        # do I just hard code the attr, or do I call a
                        # corresponding function?
                        myfunc = getattr(curblock, func_name)
                        print("myfunc: %s" % myfunc)
                        myfunc(block)

        # change the name refences in my list and dict
        self.block_name_list.remove(old_name)
        self.block_dict.pop(old_name)
        self.append_block_to_dict(new_name, block)



    def remove_block_from_menu_params(self, block_name):
        if hasattr(self, "menu_param_list"):
            match_inds = []
            #pat = block_name "."#we want to not match U2 if block name is U
            for i, row in enumerate(self.menu_param_list):
                param_str = row[0]
                if "." in param_str:
                    # assuming that "." is only in block params;
                    # if a param_str has no ".", it is a global param
                    test_name, param = param_str.split('.',1)
                    if test_name == block_name:
                        match_inds.append(i)
            if match_inds:
               match_inds.reverse()#<-- pop them backwards so that we don't shift
                                   #    the later rows up
               for ind in match_inds:
                   self.menu_param_list.pop(ind)


    def remove_block_from_print_blocks(self, block):
        if hasattr(self, "print_blocks"):
            if block in self.print_blocks:
                print("I found the block in print_blocks.")
                ind = self.print_blocks.index(block)
                self.print_blocks.pop(block)
                print("after deletion, print_blocks: %s" % self.print_blocks)



    def delete_block(self, block):
        """Remove the block from self.block_name_list and
        self.block_dict.  Also remove any references to the block from
        other blocks, such as if it is an input to another block or
        used for relative placement.  Also check in menu params and print
        blocks for any reference to the block that is to be deleted."""
        block_name = block.variable_name
        self.block_name_list.remove(block_name)
        self.block_dict.pop(block_name)

        # what is the correct approach to unplace any blocks that had
        # the deleted block as their relative block?

        # probably should add to this dict to handle
        # if/then blocks that have more/other inputs
        attr_dict = {'input_block1_name':'input_block1', \
                     'input_block2_name':'input_block2', \
                     }

        block_list = self.get_block_list()

        # check for blocks that have the block we intend to
        # delete as one of their inputs
        for curblock in block_list:
            for attr, other_attr in attr_dict.items():
                if hasattr(curblock, attr):
                    value = getattr(curblock, attr)
                    if value == block_name:
                        # set the input block instance and the input block
                        # name both to None
                        setattr(curblock, attr, None)
                        setattr(curblock, other_attr, None)
                        # we have assumed here that the input and the
                        # relative placement block are the same
                        # - not a great assumption


        # check for blocks placed relative to the block we intend
        # to delete
        for curblock in block_list:
            if hasattr(curblock, "rel_block_name"):
                if curblock.rel_block_name == block_name:
                    curblock.switch_to_abs_placement()


        # test menu_params removal, but this looks like it should work:
        self.remove_block_from_menu_params(block_name)
        # also check print blocks
        # **Note:** this code is untested because we cannot yet
        #           set the print_blocks to anything other than all
        #           the blocks, which only happens during code
        #           generation (and I don't know if it is preserved when
        #           saving to csv)
        self.remove_block_from_print_blocks(block)

        # actually delete the block
        del block


    def has_block(self, block_name):
        if block_name in self.block_dict:
            return True
        else:
            return False


    def get_block_by_name(self, block_name):
        return self.block_dict[block_name]


    def get_name_for_block(self, block):
        for name, b in self.block_dict.items():
            if b == block:
                return name


    def get_actuator_by_name(self, actuator_name):
        return self.actuators_dict[actuator_name]


    def get_sensor_by_name(self, sensor_name):
        return self.sensors_dict[sensor_name]


    def _build_block_list(self, name_list=None):
        if name_list is None:
            name_list = self.block_name_list

        block_list = [self.block_dict[name] for name in name_list]
        return block_list


    def get_block_list(self, name_list=None):
        return self._build_block_list(name_list=name_list)


    def update_block_list(self, name_list=None):
        self.block_list = self._build_block_list(name_list)


    def _get_param_list(self, attr):
        self.update_block_list()

        mylist = []

        #print("\n"*3)
        #print("attr: %s" % attr)

        print("attr: %s" % attr)

        for i, block in enumerate(self.block_list):
            print("block: %s" % block)
            if hasattr(block, attr):
                cur_val = getattr(block, attr)
                #print("%s: %s" % (block.variable_name, cur_val))
            else:
                cur_val = None
            print("cur_val:")
            print(cur_val)
            mylist.append(cur_val)

        return mylist


##    def get_lims(self, margin=3, param='x'):
##        ## Problem: margin of 3 doesn't work for
##        ## blocks that have reasonable width
##        ## - I can't just establish a margin around the center of
##        ##   each block
##        ##
##        ## New approach:
##        ## - each block should report is x and y min and max
##        ##   - or maybe top, bottom, right, and left edges
##        ## - the margin could then be smaller based on
##        ##   better numbers
##        ## - does each block get its top, bottom, left, and
##        ##   right edges set when placed?
##        mylist = self._get_param_list(param)
##        mylist2 = [item for item in mylist if item is not None]
##        myarray = np.array(mylist2)
##        mymin = myarray.min()
##        mymax = myarray.max()
##        print("mymin: %s" % mymin)
##        print("mymax: %s" % mymax)
##
##        return [mymin-margin, mymax+margin]

    def get_nonzero_param_array(self, param):
        """get param for each block, filter out those that are None,
        and then return an array

        This method is used to help find the plot limits, for example"""
        mylist = self._get_param_list(param)
        mylist2 = [item for item in mylist if item is not None]
        myarray = np.array(mylist2)
        return myarray


    def get_xlims(self, margin=1):
        """Note that the edges of the block are used for wire connections, so
        they are (x,y) pairs."""
        right_2d_array = np.array(self.get_nonzero_param_array('right_edge'))
        right_x_array = right_2d_array[:,0]
        left_2d_array = np.array(self.get_nonzero_param_array('left_edge'))
        left_x_array = left_2d_array[:,0]
        mylims = [left_x_array.min()-margin, right_x_array.max()+margin]
        return mylims


    def get_ylims(self, margin=1):
        top_2d_array = np.array(self.get_nonzero_param_array('top_edge'))
        bottom_2d_array = np.array(self.get_nonzero_param_array('bottom_edge'))
        print("top_2d_array: %s" % top_2d_array)
        print("bottom_2d_array: %s" % bottom_2d_array)
        top_y_array = top_2d_array[:,1]
        bottom_y_array = bottom_2d_array[:,1]
        mylims = [bottom_y_array.min()-margin, top_y_array.max()+margin]
        return mylims


    def find_placed_blocks(self):
        placed_blocks = []

        for block_name, curblock in self.block_dict.items():
            if curblock.placement_type:
                # not None or empty string
                placed_blocks.append(block_name)

        return placed_blocks


    def find_unplaced_blocks(self):
        unplaced_blocks = []

        for block_name, curblock in self.block_dict.items():
            if not(curblock.placement_type):
                unplaced_blocks.append(block_name)

        return unplaced_blocks


    def _find_absolute(self):
        abs_blocks = []

        # sort abs blocks first
        for block_name, curblock in self.block_dict.items():
            if curblock.placement_type == 'absolute':
                abs_blocks.append(block_name)

        return abs_blocks


    def any_absolute(self):
        abs_blocks = self._find_absolute()
        if len(abs_blocks) > 0:
            return True
        else:
            return False


    def _find_placement_order(self):
        placed_blocks = []
        relative_blocks = []

        # sort abs blocks first
        for block_name, curblock in self.block_dict.items():
            if curblock.placement_type == 'absolute':
                placed_blocks.append(block_name)
            else:
                relative_blocks.append(block_name)

        # place relative blocks now that abs blocks are placed
        #
        # iterate so that blocks are only placed when their relative
        # block is in the placed_blocks list

        unplaced_blocks = copy.copy(relative_blocks)

        for i in range(100):
            # this is a limited while(1) loop
            j = 0
            N = len(unplaced_blocks)

            if N == 0:
                break

            while (j < N):
                block_name = unplaced_blocks[j]
                curblock = self.get_block_by_name(block_name)
                rel_block_name = curblock.rel_block_name
                if rel_block_name in placed_blocks:
                    # this block is ready to place, because its relative
                    # block has already been placed
                    placed_blocks.append(block_name)
                    unplaced_blocks.remove(block_name)
                    N = len(unplaced_blocks)
                else:
                    # try next block and come back to this one on next
                    # for loop pass
                    j += 1

        return placed_blocks, unplaced_blocks



    def find_placement_order(self):
        placed_blocks, unplaced_blocks = self._find_placement_order()

        print("placed_blocks:")
        print_list(placed_blocks)

        self.placement_order = placed_blocks

        if len(unplaced_blocks) != 0:
            print("unplaced_blocks:")
            print_list(unplaced_blocks)

        return placed_blocks, unplaced_blocks


    def update_relative_block_placements(self):
        """Update the relative positions of blocks before drawing, in
        case something has changed using the gui (for example).

        This only works if the blocks are sorted in a correct
        placement order.

        Note that this assumes all blocks have been placed in a valid
        way have have rel_block defined.
        """
        self.find_placement_order()
        for name in self.placement_order:
            curblock = self.get_block_by_name(name)
            curblock.update_relative_placement()


    def refresh_block_placements(self):
        """Trying to create a function to call after something that
        was broken in a block diagram has been fixed.  This assumes
        that a valid placement order can be found and all relative blocks
        at least know the name of the blocks they are relative to."""
        placed_blocks, unplaced_blocks = self.find_placement_order()

        rel_params = ["rel_pos", "rel_distance", "xshift", "yshift"]

        for block_name in placed_blocks:
            curblock = self.get_block_by_name(block_name)
            if curblock.placement_type == 'relative':
                rel_block_name = curblock.rel_block_name
                rel_block = self.get_block_by_name(rel_block_name)
                kwargs = {}
                for key in rel_params:
                    kwargs[key] = getattr(curblock,key)
                curblock.place_relative(rel_block, **kwargs)


    def draw(self, update_rel=True, colorful_wires=False):
        # I need to force a more robust check here for
        # placement validity.
        if self.ax is None:
            fig = plt.figure(figsize=(9,9))
            self.ax = fig.add_subplot(111)

        if update_rel:
            self.update_relative_block_placements()

        wire_colors=['k','g','r','b','c','m','y']*10
        i=0
        for block in self.get_block_list():
            print("drawing: %s" % block.variable_name)
            #>>>> I suspect isplaced lies if the block
            #>>>> was placed but something has broken.
            #>>>> ?how do I check for broken placement?
            if block.isplaced():#<-- can I do a better test here?
                # isplaced checks for a placement type, x, and y params
                # --> that seems pretty good
                # ? how are my students getting errors about a block
                # ? not having x or y params?

                # pass wire color here if specified:
                if colorful_wires:
                    wire_color=wire_colors[i]
                else:
                    wire_color = 'k'
                block.draw(self.ax, wire_color=wire_color)
                i += 1


        # output variable labels
        for vstr, block in self.output_variables:
            output_dir = block.guess_output_direction()
            extra = 0.1*len(vstr)
            if output_dir == 'right':
                label_x = block.x + (block.width)*0.5 + 0.5 + extra
            else:
                label_x = block.x - (block.width)*0.5 - 0.5 - extra
            label_y = block.y + 0.5
            self.ax.text(label_x, label_y, \
                         vstr, fontdict=self.fontdict, \
                         ha='center', va='center')



    def draw_arrow(self, start_coords, end_coords, \
                   fc='k', ec=None, lw=None, **plot_args):
        if 'wire_color' in plot_args:
            fc = plot_args.pop('wire_color')

        if not hasattr(self, 'hw'):
            self.set_arrow_lengths()
        if ec is None:
            ec = fc
        # if lw is None:
        #     lw = self.arrow_lw
        ##start_A = transform_coords(start_coords, HT)
        ##stop_A = transform_coords(end_coords, HT)
        dx = end_coords[0]-start_coords[0]
        dy = end_coords[1]-start_coords[1]

        self.ax.arrow(start_coords[0], start_coords[1], dx, dy, \
                      lw=lw, fc=fc, ec=ec, \
                      width=0.01, \
                      head_width=self.hw, head_length=self.hl, \
                      #overhang = self.ohg, \
                      length_includes_head=True, clip_on = False, \
                      **plot_args)



    def axis_off(self):
        self.ax.set_axis_off()


    def get_arduino_init_code(self, indent=None):
        #listout = []
        #for block in self.get_block_list():#<---- self.block_list no longer works
        #    print("block: %s" % block)
        #    new_list = block.get_arduino_init_code()
        #    listout.extend(new_list)
        #return listout
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_init_code", \
                                                   indent=indent)
        return mylist



    def get_arduino_code_one_section(self, \
                                     method_name="get_arduino_init_code", \
                                     indent=None, \
                                     block_list=None):
        """This code exists to make it easier to get code from blocks
        for different sections of the Arduino template.  This is done by
        calling method_name for each block.

        method_name refers to the method to call for each block to get
        the code for the section for each block."""
        if block_list is None:
            block_list = self.get_block_list()
        listout = []
        for block in block_list:
            myfunc = getattr(block, method_name)
            new_list = myfunc()
            listout.extend(new_list)

        if indent is not None:
            listout = [indent + line for line in listout]
        return listout


    def get_arduino_setup_code(self, indent=None):
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_setup_code", \
                                                   indent=indent)
        return mylist


    def get_arduino_loop_code(self, indent=None):
        ## Always re-check the execution_order
        #if not hasattr(self, "execution_order"):
        #    self.find_execution_order()
        self.find_execution_order()

        block_list = self.execution_order

        mylist = self.get_arduino_code_one_section(method_name="get_arduino_loop_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        mylist2 = self.get_arduino_code_one_section(method_name="get_arduino_secondary_loop_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        # I think I need to get the secondary loop code here
        # - one wrinkle is that the main loop code and the secondary loop
        #   code replace the same string in the template
        #   - so, I need one big list to insert there
        return mylist + mylist2


    def _get_menu_param_code(self, \
                             float_func="get_float_with_message_no_pointer", \
                             int_func="get_int_with_message_no_pointer", \
                            ):
        # return empty list if we don't have a list of params for the menu
        if not hasattr(self, "menu_param_list"):
            return []
        elif len(self.menu_param_list) == 0:
            return []

        code = []
        out = code.append

        for full_var, int_only in self.menu_param_list:
            pat = '%s = %s("%s");'
            if int_only:
                myfunc = int_func
            else:
                myfunc = float_func
            outstr = pat % (full_var, myfunc, full_var)
            out(outstr)

        return code


    def _get_menu_param_code_rpi(self):
        code = self._get_menu_param_code(float_func="get_float")
        return code


    def get_arduino_menu_code(self, indent=None):
        print("in get_arduino_menu_code, indent=%s$" % indent)
        menu_param_code = self._get_menu_param_code()
        if indent:
            menu_param_code = [indent + item for item in menu_param_code]
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_menu_code", \
                                                   indent=indent)
        # add code for menu parameters here
        outlist = menu_param_code + mylist
        return outlist


    def get_arduino_menu2_code(self, indent=None):
        print("in get_arduino_menu2_code, indent=%s$" % indent)
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_menu2_code", \
                                                   indent=indent)
        return mylist


    def get_arduino_menu3_code(self, indent=None):
        print("in get_arduino_menu3_code, indent=%s$" % indent)
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_menu3_code", \
                                                   indent=indent)
        return mylist



    def get_rpi_menu_code(self, indent=None):
        menu_param_code = self._get_menu_param_code_rpi()
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_menu_code", \
                                                   indent=indent)
        # add code for menu parameters here
        outlist = menu_param_code + mylist
        return outlist


    def append_menu_param_from_block(self, block, param_name, int_only=0):
        """add a parameter to the list of parameters that will be
        requested over serial in the menu function.  This would be
        used for example with PID tuning: Kp, Ki, and Kd would all be
        easily adjusted without reprogramming the Arduino.

        block is the block instance from Python whose parameter we are
        setting.  param_name is the name of the block attribute that
        will be set.  If int_only is not zero, use a get_int method in
        Arduino, otherwise get a float."""
        if not hasattr(self, "menu_param_list"):
            self.menu_param_list = []

        assert hasattr(block, param_name), "the block does not have a parametered called %s" % param_name
        full_var = "%s.%s" % (block.variable_name, param_name)
        cur_tuple = (full_var, int_only)
        self.menu_param_list.append(cur_tuple)



    def append_menu_param_global_variable(self, variable_name, int_only=0):
        if not hasattr(self, "menu_param_list"):
            self.menu_param_list = []
        cur_tuple = (variable_name, int_only)
        self.menu_param_list.append(cur_tuple)


    def get_arduino_welcome_code(self, indent='   '):
        line1 = 'Serial.println("%s");' % self.welcome_msg
        return [indent + line1]


    def set_print_blocks(self, block_list):
        """Set the blocks that will print their output when run from
        Arduino or micropython.  Note that block_list must be a list
        of block instances."""
        self.print_blocks = block_list


    def set_print_blocks_from_names(self, block_name_list):
        """Look up each name in block_name_list in self.block_dict
        using the function self.get_block_by_name.  Then pass the list
        of block instances to self.set_print_blocks."""
        block_list = []
        for name in block_name_list:
            # name can actually refer to a block or a sensor, both of
            # which are allowed as print_blocks
            if name in self.block_dict:
                block = self.get_block_by_name(name)
                block_list.append(block)
            elif name in self.sensors_dict:
                sensor = self.get_sensor_by_name(name)
                block_list.append(sensor)
        self.set_print_blocks(block_list)


    def find_single_output_blocks_and_sensors(self):
        """When setting the printable blocks or the blocks that can be
        used as input for other blocks, the list needs to be filtered
        to only blocks that have one output.  Plants with more than
        one input are handled by allowing sensors to also be treated
        as blocks."""
        so_blocks = []
        all_block_names = copy.copy(self.block_name_list)

        for block_name in all_block_names:
            block = self.get_block_by_name(block_name)
            if not isinstance(block, plant_with_double_actuator_two_sensors):
                so_blocks.append(block_name)

        # append all sensor names (might need to revisit later)
        so_blocks += self.sensor_name_list
        self.single_output_blocks = so_blocks
        return so_blocks


    def get_arduino_print_code(self, indent='    '):
        print("in get_arduino_print_code")
        if hasattr(self, "print_blocks") and len(self.print_blocks) >0:
            # only print the output of some specified list of blocks
            block_list = self.print_blocks
        else:
            # print the output of all blocks
            print("using all blocks as print blocks (hopefull)")
            block_list= self.get_block_list()
        print("block_list: %s" % block_list)
        mylist = self.get_arduino_code_one_section(method_name="get_arduino_print_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        return mylist


    def get_csv_labels_line(self, arduino=False):
        if hasattr(self, "print_blocks") and len(self.print_blocks) > 0:
            # only print the output of some specified list of blocks
            block_list = self.print_blocks
        else:
            # print the output of all blocks
            block_list= self.get_block_list()


        if arduino:
            mylabels = ['t_ms']
        else:
            mylabels = ['i','t_ms']

        for block in block_list:
            curlabel = block.get_csv_label()
            mylabels.append(curlabel)

        mystr = ",".join(mylabels)
        return mystr


    def get_csv_labels_as_list(self):
        mystr = self.get_csv_labels_line()
        return [mystr]


    def arduino_label_print_line(self, indent=None):
        mystr = self.get_csv_labels_line(arduino=True)
        print("mystr = %s" % mystr)
        print_line = 'Serial.print("%s");' % mystr
        line2 = "mynewline();"
        listout = [print_line, line2]

        if indent:
            listout = [indent + line for line in listout]
        return listout



    def rpi_label_list(self, indent=None):
        mystr = self.get_csv_labels_line()
        fprint_line = 'fprintf(fp, "%s\\n", "' + mystr + '");'
        if indent:
            fprint_line = indent + fprint_line
        return [fprint_line]


    def get_rpi_print_code(self, indent=None):
        if hasattr(self, "print_blocks"):
            # only print the output of some specified list of blocks
            block_list = self.print_blocks
        else:
            # print the output of all blocks
            block_list= self.get_block_list()

        num_print = len(block_list)
        # Note that the first two things in each row are the loop counter
        # variable and the time in ms (with two decimels)
        fmt_str = "%i,%0.2f" + ",%i"*num_print + "\\n"

        fprint_line = 'fprintf(fp, "%s",' % fmt_str
        #plan: generate a string of the form "fprint_line(fp, fmt_str, arg);"
        arg = 'i,t_ms'
        # Randbom note: I am locked into the assumption that each block returns
        # an integer.  What could go wrong?
        for block in block_list:
            arg += ','
            curstr = block.get_rpi_print_string()
            arg += curstr

        fprint_line += arg + ');'

        if indent:
            fprint_line = indent + fprint_line
        return [fprint_line]




    def generate_arduino_code(self, output_name, \
                              template_path, \
                              output_folder='', \
                              verbosity=0):
        """Read in the Arduino template file and replace various
        strings with the associated lines for the block diagram system
        (init, setup, loop, menu, ...)"""
        # - how do I find the template?
        #     - I don't want to have them pass in a path most of the time.
        #     - how would I get them a default template?
        #         - can pip do this?
        #     - different applications will likely require different templates
        #         - punt for now and require a template path
        # - do I want to depend on txt_mixin?
        #     - is figuring out how to help students use the code essential right now?
        #     - dependencies in setuputils are easy


        # plan:
        # - find search strings
        # - call associated method to get auto-gen code
        # - insert code where string used to be
        # - repeat
        #     - use a list of tuples (search string, method) to do this repeatedly
        #
        #
        # using list slicing
        # to insert one list in another
        #test_list[pos:pos] = insert_list

        self.arduino_file = txt_mixin.txt_file_with_list(template_path)

        tup_list = [("bdsysinitcode", self.get_arduino_init_code), \
                    ("bdsyssetupcode", self.get_arduino_setup_code), \
                    ("bdsysmenucode", self.get_arduino_menu_code), \
                    ("bdsysloopcode", self.get_arduino_loop_code), \
                    ("bdsyscsvlabels", self.arduino_label_print_line), \
                    ("bdsysprintcode", self.get_arduino_print_code), \
                    ("bdsyswelcomecode", self.get_arduino_welcome_code), \
                    ("bdsysmenu2", self.get_arduino_menu2_code), \
                    ("bdsysmenu3", self.get_arduino_menu3_code), \
                    ]

        mylist = self.arduino_file.list


        optional_list = ["bdsysmenu2", "bdsysmenu3"]

        for search_str, method in tup_list:
            ind = mylist.find(search_str)#<-- can I make this fail elegantly
                                         #    under certain conditions?
                                         #    - do I add a third element to the
                                         #      tuple for required or optional?
            if ind is None:
                msg1 = "did not find %s in mylist" % search_str
                print(msg1)
                print("template_path: %s" % template_path)
                if search_str not in optional_list:
                    raise ValueError(msg1)

            else:
                matchline = mylist[ind]
                print("match line:%s" % matchline)
                myindent, rest = matchline.split('/',1)

                new_ind = ind+1
                mylist.insert(new_ind,"")
                new_code = method(indent=myindent)#<-- pass args here, including indent
                self.arduino_file.list[new_ind:new_ind] = new_code
                if verbosity > 0:
                    print('\n')
                    print(search_str)
                    print('='*20)
                    for line in new_code:
                        print(line)
                    print('\n'*2)


        # save:
        curdir = os.getcwd()
        if output_folder:
            os.chdir(output_folder)
        if not os.path.exists(output_name):
            os.mkdir(output_name)
        outpath = os.path.join(output_name, output_name+'.ino')
        self.arduino_file.save(outpath)

        os.chdir(curdir)


    def get_rpi_loop_code(self, indent=None):
        #if not hasattr(self, "execution_order"):
        self.find_execution_order()

        block_list = self.execution_order

        mylist = self.get_arduino_code_one_section(method_name="get_rpi_loop_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        mylist2 = self.get_arduino_code_one_section(method_name="get_rpi_secondary_loop_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        # I think I need to get the secondary loop code here
        # - one wrinkle is that the main loop code and the secondary loop
        #   code replace the same string in the template
        #   - so, I need one big list to insert there
        return mylist + mylist2


    def get_rpi_end_test_code(self, indent=None):
        block_list = self.execution_order

        mylist = self.get_arduino_code_one_section(method_name="get_rpi_end_test_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        return mylist


    def get_rpi_start_test_code(self, indent=None):
        block_list = self.execution_order

        mylist = self.get_arduino_code_one_section(method_name="get_rpi_start_test_code", \
                                                   indent=indent, \
                                                   block_list=block_list)
        return mylist


    def generate_rpi_code(self, output_path, \
                          template_path, \
                          verbosity=0, no_cal=False):
        """Read in the Raspberry Pi template file and replace various
        strings with the associated lines for the block diagram system
        (init, setup, loop, menu, ...)"""
        # - how do I find the template?
        #     - I don't want to have them pass in a path most of the time.
        #     - how would I get them a default template?
        #         - can pip do this?
        #     - different applications will likely require different templates
        #         - punt for now and require a template path
        # - do I want to depend on txt_mixin?
        #     - is figuring out how to help students use the code essential right now?
        #     - dependencies in setuputils are easy


        # plan:
        # - find search strings
        # - call associated method to get auto-gen code
        # - insert code where string used to be
        # - repeat
        #     - use a list of tuples (search string, method) to do this repeatedly
        #
        #
        # using list slicing
        # to insert one list in another
        #test_list[pos:pos] = insert_list

        self.rpi_file = txt_mixin.txt_file_with_list(template_path)

        ## how to handle indentation well?
        ## - matching the indentation of the search string line
        ##   seems like a code
        ##   - note that the search string almost certainly has a comment
        ##     symbol in front of it
        ##
        ## Complications:
        ## - I handle indent differently in different methods
        ## - some methods call get_arduino_code_one_section, and some do not
        ##
        ## Conclusion:
        ## - this is a bit of a mess
        ##
        ## How should indent work?
        ## - find proper indent in the loop below based on the line
        ##   containing the search string
        ##   - all templates **must** put the search string at proper indent
        ## - pass indent to method(indent=indent) in the loop below
        ##   - all methods **must** take indent as a kwargs
        tup_list = [("bdsysinitcode", self.get_arduino_init_code), \
                    ("bdsyssetupcode", self.get_arduino_setup_code), \
                    ("bdsysmenucode", self.get_rpi_menu_code), \
                    ("bdsysloopcode", self.get_rpi_loop_code), \
                    ("bdsyscsvlabels", self.rpi_label_list), \
                    ("bdsysprintcode", self.get_rpi_print_code), \
                    ("bdsysendtestcode", self.get_rpi_end_test_code), \
                    ("bdsysstarttestcode", self.get_rpi_start_test_code), \
                    #("bdsyswelcomecode", self.get_arduino_welcome_code), \
                    ]

        if no_cal:
            mylist = hard_code_cal(self.rpi_file)
        else:
            mylist = self.rpi_file.list

        print('='*20)
        print("mylist aroun 190:")
        for i in range(185, 195):
            print(mylist[i])
        print('='*20)


        p_indent = re.compile(r"^(\s*)")

        for search_str, method in tup_list:
            ind = mylist.find(search_str)
            # use regexp here to find whitespace at beginning of line ind
            print("search_str: %s, ind: %s" % (search_str, ind))
            if not ind:
                print("did not find a match for %s" % search_str)
            match_line = mylist[ind]
            q_indent = p_indent.search(match_line)
            if q_indent is not None:
                indent = q_indent.group(1)
            else:
                indent = ''
            # pass indent to method below
            new_ind = ind+1
            mylist.insert(new_ind,"")
            new_code = method(indent=indent)
            mylist[new_ind:new_ind] = new_code
            if verbosity > 0:
                print('\n')
                print(search_str)
                print('='*20)
                for line in new_code:
                    print(line)
                print('\n'*2)


        # save:
        self.rpi_file.save(output_path)



    def get_python_pre_code(self, indent=""):
        """Generate the code that goes before any block init code."""
        # What is the right answer for multiple loops?
        # - handle the N's for each loop in the templte?
        # - assume students leave the template alone and set N's in the gui?
        #     - maybe in the set loop numbers dialog
        #     - this would become another gui param to be saved and loaded
        #         - oh well
        if self.has_loops:
            if hasattr(self, "N1"):
                N1 = self.N1
            else:
                N1 = 1000
            if hasattr(self, "N2"):
                N2 = self.N2
            else:
                N2 = 200

            line1 = "N1 = %i" % N1
            line2 = "N2 = %i" % N2
            line3 = "num_read = np.zeros(N1)"
            line4 = "prev_check = -1"
            listout = [line1,line2,line3,line4]
        else:
            line1 = "N = %i" % self.N
            line2 = "num_read = np.zeros(N)"
            line3 = "prev_check = -1"
            listout = [line1,line2,line3]

        return listout


    def get_code_from_object_list_one_method(self, object_list, method_name="get_python_init_code", \
                                             indent=None):
        """This code exists to make it easier to get code from
        sensors, actuators, or blocks for different sections of the
        Python template.

        method_name refers to the method to call for each object
        (sensor, actuator, or block) to get the code for the section
        for each block.

        object_list must contain a list of sensors, actuator, or blocks that have a method by the
        name assigned to method_name."""
        listout = []
        for thing in object_list:
            myfunc = getattr(thing, method_name)
            new_list = myfunc()
            #listout.append("# %s" % type(block))
            listout.extend(new_list)


        if indent is not None:
            listout = [indent + line for line in listout]
        return listout


    def get_code_from_blocks_one_method(self, method_name="get_python_init_code", \
                                        indent=None, \
                                        block_list=None, **kwargs):
            """This code exists to make it easier to get code from blocks
            for different sections of the Python template.

            method_name refers to the method to call for each block to get
            the code for the section for each block.

            block_list is optional and allows code to be generated in
            a specific order or for only a subset of blocks."""
            if block_list is None:
                block_list = self.get_block_list()

            print('in get_code_from_blocks_one_method')
            print("kwargs: %s" % kwargs)
            listout = []
            for block in block_list:
                myfunc = getattr(block, method_name)
                new_list = myfunc(**kwargs)
                #listout.append("# %s" % type(block))
                listout.extend(new_list)


            if indent is not None:
                listout = [indent + line for line in listout]
            return listout


    def get_loop_blocks(self, loop_num):
        all_blocks = self.get_block_list()
        loop_blocks = []
        for curblock in all_blocks:
            # Note: this will throw an error if the block doesn't have
            # a loop_number parameter.  This method should only be
            # called if the block diagram has loops.
            if curblock.loop_number == loop_num:
                loop_blocks.append(curblock)
        return loop_blocks


    def get_code_from_blocks_one_method_with_loops(self, method_name="get_python_init_code", \
                                                   kwargs_list=[], \
                                                   indent=None, \
                                                   block_list=None):
        """Call the method method_name for each block after dividing
        the blocks into groups for each loop.  For each loop, pass in
        the next kwarg in kwargs_list."""
        listout = []
        print('='*20)
        print('\n')
        print("in get_code_from_blocks_one_method_with_loops")
        for i in range(1, self.max_loops + 1):
            j = i - 1
            kwargs = kwargs_list[j]
            block_list = self.get_loop_blocks(i)
            print("i = %i" %i)
            print("block_list:")
            print_block_names(block_list)
            print("kwargs: %s" % kwargs)
            loop_list = self.get_code_from_blocks_one_method(method_name=method_name, \
                                                             indent=indent, \
                                                             block_list=block_list, **kwargs)
            listout.extend(loop_list)
        print('\n')
        print('='*20)
        return listout


    def get_sensor_list(self):
        sensors = []
        for key in self.sensor_name_list:
            cur_sense = self.sensors_dict[key]
            sensors.append(cur_sense)
        return sensors


    def get_block_python_init_code(self, indent=""):
        sensor_list = self.get_sensor_list()
        mylist = []
        if sensor_list:
            mylist_s = self.get_code_from_object_list_one_method(sensor_list,"get_python_init_code", \
                                                                 indent=indent)
            mylist += mylist_s
        mylist_b = self.get_code_from_blocks_one_method("get_python_init_code", indent=indent)
        mylist += mylist_b
        return mylist


    def get_block_secondary_init_code(self, indent=""):
        # How do I handle this with multiple loops?
        # - have a for loop that executes for the number of loops?
        # - for init code, there are differences for the loops,
        #   but all the code goes in the same spot
        # - for loop code, the code from each loop goes in a different spot

        # big idea:
        # - the BD system should get the appropriate code from the appropriate blocks
        # - the system should then put the code in the correct places
        # - what method am I calling for each block?
        # - which blocks am I calling it on?
        # - what parameters am I passing in?

        # what is the right way to handle secondary init code for each loop?
        # - for blocks in loop 1, cqll the method with Nstr="N1"
        print("in get_block_secondary_init_code, has_loops = %s" % self.has_loops)

        if self.has_loops:
            # - find the blocks for each loop
            # - call the method for each loop with the Nstr kwarg
            kwargs_list = [{"Nstr":"N1"}, {"Nstr":"N2"}, {"Nstr":"N3"}]
            mylist = self.get_code_from_blocks_one_method_with_loops("get_python_secondary_init_code", \
                                                                     kwargs_list=kwargs_list)
        else:
            mylist = self.get_code_from_blocks_one_method("get_python_secondary_init_code")
        return mylist


    def get_python_loop_code(self, indent="    "):
        if hasattr(self, "execution_order"):
            block_list = self.execution_order
        else:
            block_list = None

        # this function assumes there are no numbered loops in code,
        # i.e. all loop code gets executed at one time in one big loop
        # with index i.

        mylist = self.get_code_from_blocks_one_method("get_python_loop_code", \
                                                      indent=indent, \
                                                      block_list=block_list)
        return mylist


    def get_python_secondary_loop_code(self, indent="    "):
        if hasattr(self, "execution_order"):
            block_list = self.execution_order
        else:
            block_list = None
        mylist = self.get_code_from_blocks_one_method("get_python_secondary_loop_code", \
                                                      indent=indent, \
                                                      block_list=block_list)
        return mylist


    ## def find_execution_order(self, high_priority_blocks=[]):
    ##     """create the parameter self.execution_order which is the list
    ##     of the blocks in the order that their loop code should be
    ##     executed in the main loop.  high_priority_blocks will be first
    ##     and the remaining blocks from self.get_block_list() will be later."""
    ##     other_blocks = [block for block in self.get_block_list() if block not in high_priority_blocks]
    ##     self.execution_order = high_priority_blocks + other_blocks

    def find_execution_order(self, block_list=None, loop_num=None):
        """Determine the order that blocks should execute inside the
        loop.  Constants, inputs, and sources should be first (inputs
        and sources might be the same thing).  Plants that read their
        sensors from an Arduino over i2c or something should be next.

        Once you have added blocks with no inputs, go through the
        remaining blocks and check to see if the input(s) for a block
        are already in the execution list.  A block is ready to be
        added if its input(s) are already in.  If not, skip the block
        and try it later.

        - how do we handle this if there is more than one loop?

            - it seems like each loop has to have an acceptable
              execution order with its subset of blocks

            - allowing the possiblity of passing in a block subset to
              make it easier to handle loops separetely later"""
        verbosity = 1
        if verbosity > 0:
            print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            print("")
            print("in find_execution_order")
            print("")
            print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        # how do I handle cases where the input block is a sensor from
        # a plant with multiple i2c sensors?
        if block_list is None:
            # default to all blocks if block_list is not passed in
            block_list = self.get_block_list()

        exec_order = []
        sensor_list = []# list of sensors whose plants are in exec_order
        all_blocks = copy.copy(block_list)
        remaining_blocks = []

        # find blocks that have no inputs: inputs, sources, constants,
        # - some plants might effectively have no inputs from other blocks
        #   if they are reading from sensors or if sensor reading is done before
        #   sending commands to the actuators


        for block in block_list:
            if isinstance(block, no_input_block) or block.no_input:
                exec_order.append(block)
            else:
                remaining_blocks.append(block)


        print("after no input stuff, exec_order = %s" % exec_order)
        print("remaining_blocks = %s" % remaining_blocks)

        # an early plant is a plant that can be called early in the
        # loop, I think this means that the sensor values can be
        # read separately from sending the actuator signals
        #### (old): because it effectively has no inputs (its inputs are
        #### read from an Arduino, probably over i2c)
        early_plant_classes = [plant, \
                               plant_with_two_i2c_inputs_and_two_i2c_sensors, \
                               plant_with_double_actuator_two_sensors, \
                               cart_pendulum]

        remaining_stage_2 = copy.copy(remaining_blocks)

        def is_early_plant(block):
            for plant_class in early_plant_classes:
                if isinstance(block, plant_class):
                    return True

        sensor_attrs = ['sensor','sensor1','sensor2']

        for block in remaining_stage_2:
            if is_early_plant(block):
                exec_order.append(block)
                for attr in sensor_attrs:
                    if hasattr(block, attr):
                        mysensor = getattr(block, attr)
                        sensor_list.append(mysensor)
                remaining_blocks.remove(block)

        # at this point, all blocks with no inputs have been put in
        # exec_order and remaining_blocks contains only the blocks
        # whose order is still uncertain



        # a loop_variable is like a zoh block from another (probably
        # slower) loop

        # - loop_variable blocks should be considered "alread in" the
        #   exec order, so I need to add all the loop_variable blocks
        #   from other loops to the other_blocks list

        # other_blocks will hold the blocks from other loops that are
        # ok inputs as far as exec_order is concerned
        other_blocks = []

        self.update_block_list()

        for curblock in self.block_list:
            if isinstance(curblock, loop_variable):
                other_blocks.append(curblock)


        # I need to build a full list of blocks and sensors from other loops if
        # loop_num > 0.

        other_sensors = []
        if loop_num is not None:
            if loop_num > 1:
                for i in range(1,loop_num):
                    attr_i = "execution_order_loop_%i" % i
                    blocks_i = getattr(self, attr_i)
                    other_blocks += blocks_i

                # get the sensors associated with other_blocks:
                for block in other_blocks:
                    if is_early_plant(block):
                        for attr in sensor_attrs:
                            if hasattr(block, attr):
                                mysensor = getattr(block, attr)
                                other_sensors.append(mysensor)

                print("other_blocks:")
                print_block_names(other_blocks)
                print("other_sensors: %s" % other_sensors)


        # try to sort them 100 times and then give up
        for i in range(100):
            # go over each block in remaining_blocks and see if all of
            # its inputs are already in exec_order
            if len(remaining_blocks) == 0:
                break

            j = 0
            N = len(remaining_blocks)
            print("i = %i, j = %i, N = %i" % (i,j,N))

            while (j<N):
                curblock = remaining_blocks[j]
                print("j = %i, N = %i, curblock = %s" % (j, N, curblock.variable_name))
                if check_for_inputs_in_block_list(curblock, exec_order, sensor_list, \
                                                  other_blocks=other_blocks, \
                                                  other_sensors=other_sensors):
                    # the input(s) for curblock are in and it is safe
                    # to append curblock to exec_order
                    print("success")
                    exec_order.append(curblock)
                    remaining_blocks.remove(curblock)
                    N = len(remaining_blocks)# remaining_blocks is now shorter by 1
                else:
                    # curblock's input(s) are not in exec_order yet,
                    # so we need to skip it for now
                    # - try the next block
                    print("failure, incrementing j")
                    j += 1


        if len(remaining_blocks) == 0:
            print("successful sorting of exec_order:")
            print_block_names(exec_order)
            if loop_num is None:
                self.execution_order = exec_order#<--- we only want to do this if there is only one loop
            else:
                attr = "execution_order_loop_%i" % loop_num
                setattr(self, attr, exec_order)
            return exec_order
        else:
            print("exec_order sorting failed.....")
            print("")
            print("exec_order:")
            print_block_names(exec_order)
            print("remaining_blocks:")
            print_block_names(remaining_blocks)






    def get_python_plotting_code(self, indent=""):
        # Steps:
        # - create time vector
        # - create plot for each plot specified in self.plot_list
        #     - self.plot_list is a list of desired plots, where each plot
        #       is specified as a list of variable names or blocks whose
        #       outputs are to be plotted
        if len(self.plot_list) == 0:
            # do nothing
            return []
        line1 = "nvect = np.arange(N)"
        line2 = "dt = %0.6g" % self.dt
        line3 = "t = nvect*dt"
        line4 = ""
        plot_header = [line1, line2, line3, line4]

        variable_code = self.get_output_variable_code()

        code = []

        for cur_plot in self.plot_list:
            cur_code = cur_plot.get_python_code()
            code.extend(cur_code)

        return plot_header + variable_code + code


    def add_plot(self, plotlist, fignum=None, **kwargs):
        """Create a plot that will be added to the auto-generated
        python code.  plotlist should be either a list of output
        variables that are defined in the plotting code or a list of
        blocks whose output_vectors are to be plotted.

        See plot_code_generator for kwarg options (xlim, ylim, xlabel,
        ylabel, title, ...)"""
        curplot = plot_code_generator(plotlist, fignum=fignum, **kwargs)
        self.plot_list.append(curplot)


    def define_output_variables(self, tup_list):
        """Create easier to read variables in the code after the loop
        for use in plotting.  tup_list is a list of tuples whose first
        element is the short variable name and the second element is
        the block whose output_vector the variable name will be
        associated with:

        [('u', u_block), ('e', sum1_block), ....]"""
        self.output_variables = tup_list


    def get_output_variable_code(self, indent=""):
        if len(self.output_variables) == 0:
            #do nothing
            return []

        code = []

        for vstr, block in self.output_variables:
            line = "%s = %s.output_vector" % (vstr, block.variable_name)
            code.append(line)

        code.append('')

        return code

    def set_sensor_loop_numbers(self):
        """In order for printing to work correctly, we need any
        sensors that are in self.print_blocks to know their loop_num
        (if the block diagram includes mulitple loops).  In order to
        do this, each block needs to share its loop_num with its
        sensors (if any)."""
        # Approach:
        #
        # - if the block_diagram does not have loops, do nothing
        # - else, find all blocks and iterate over them
        # - for each block, if it has a sensor, assign the block's
        #   loop_num to the sensor
        if self.has_loops:
            self.update_block_list()
            all_blocks = self.get_block_list()
            sensor_attrs = ['sensor','sensor1','sensor2']
            for curblock in all_blocks:
                for attr in sensor_attrs:
                    if hasattr(curblock, attr):
                        mysensor = getattr(curblock, attr)
                        mysensor.loop_number = curblock.loop_number


    def gen_micropython_printing_code_one_loop(self, indent="", Nstr="N", istr="i", loop_num=None):
        ## Micropython printing code:
        ## print_blocks = [u_pulse_block, add_block1, subtract_block1, line_sense]
        pb_str = ""
        if loop_num is None:
            pb_blocks = self.print_blocks
        else:
            # get the pring blocks that are also in the current loop
            # - also get the sensors associated with the current loop
            #     - this might be trickier
            self.set_sensor_loop_numbers()
            # how do I determine the loop number for a sensor?
            # - does a sensor know its loop number?
            # - does a sensor know its plant?
            pb_blocks = [block for block in self.print_blocks if block.loop_number == loop_num]
            if not pb_blocks:
                # loop 3 is probably empty
                return []

            print("p"*10)
            print("\n")
            print("loop_num: %i" % loop_num)
            print("print blocks for loop:")
            print_block_names(pb_blocks)
            print("\n")
            print("p"*10)


        for cur_block in pb_blocks:
            if pb_str:
                pb_str += ", "
            pb_str += cur_block.variable_name

        pb_line = "print_blocks = [%s]" % pb_str
        print_lines = [pb_line]
        out = print_lines.append

        if loop_num is not None:
            out("print('loop_num: %i')" % loop_num)
        else:
            out("print('#begin test')")

        out("for %s in range(%s):" % (istr, Nstr))
        out("    rowstr = str(%s)" % istr)
        out("    for block in print_blocks:")
        out("        if rowstr:")
        out("            rowstr += ', '")
        out("        rowstr += str(block.read_output(%s))" % istr)
        out("    print(rowstr)")
        return print_lines



    def gen_micropython_printing_code(self, indent="", Nstr="N", istr="i"):
        ## Micropython printing code:
        ## print_blocks = [u_pulse_block, add_block1, subtract_block1, line_sense]
        if self.has_loops:
            print_list = []
            loop_vars = ['i','j','k']
            for i in range(1, self.max_loops + 1):
                if print_list:
                    print_list.append("")
                Nstr = "N%i" % i
                istr = loop_vars[i-1]
                curlist = self.gen_micropython_printing_code_one_loop(indent="", \
                                                                      Nstr=Nstr, istr=istr, \
                                                                      loop_num=i)
                print_list += curlist

            return print_list
        else:
            return self.gen_micropython_printing_code_one_loop(indent="", Nstr="N", \
                                                               istr="i", loop_num=None)

        ## pb_str = ""
        ## for cur_block in self.print_blocks:
        ##     if pb_str:
        ##         pb_str += ", "
        ##     pb_str += cur_block.variable_name

        ## pb_line = "print_blocks = [%s]" % pb_str
        ## print_lines = [pb_line]
        ## out = print_lines.append

        ## out("for i in range(N):")
        ## out("    rowstr = str(i)")
        ## out("    for block in print_blocks:")
        ## out("        if rowstr:")
        ## out("            rowstr += ', '")
        ## out("        rowstr += str(block.read_output(i))")
        ## out("    print(rowstr)")
        ## return print_lines

    def clear_loops(self):
        self.update_block_list()
        all_blocks = self.get_block_list()
        for curblock in all_blocks:
            if hasattr(curblock, "loop_number"):
                curblock.loop_number = None


    def check_for_loops(self):
        """Check to see if any blocks have been assigned a
        loop_number.  If any blocks have loop_numbers, then they all
        must."""
        print("in check_for_loops")
        any_loops = False
        all_blocks = self.get_block_list()
        for curblock in all_blocks:
            if hasattr(curblock, "loop_number"):
                if curblock.loop_number:
                    any_loops = True
                    break

        if not any_loops:
            self.has_loops = False
            print("no loops found")
            return False

        # if we get to this point, at least one block has a
        # loop_number, so they all must for code generation to work
        # correctly
        all_have_loops = True
        for curblock in all_blocks:
            if not hasattr(curblock, "loop_number") or not curblock.loop_number:
                all_have_loops = False
                break

        assert all_have_loops, "Not all blocks have valid loop numbers"

        # if we make it to this point, all blocks have valid loop numbers
        print("has_loops = True")
        self.has_loops = True
        return True


    def get_python_secondary_loop_code_one_loop(self, loop_num=1, loop_var='i', indent="    "):
        return self.get_python_code_one_loop(method_name="get_python_secondary_loop_code", \
                                     loop_num=loop_num, loop_var=loop_var, \
                                     indent=indent)


    def get_python_code_one_loop(self, method_name="get_python_loop_code", \
                                 loop_num=1, loop_var='i', \
                                 indent="    "):
        """This is the function for the loop code if there are
        multiple loops (i.e. code running at multiple frequencies).
        This was first written to accomidate the cart/pendulum
        experiment in EGR 345 where the line sensor takes 5-10ms to
        read so that line following control needs to execute at 100 Hz
        while pendulum vibration suppression or inverted pendulum
        balancing needs to run at 250-500 Hz.

        What steps are needed for each loop?

        - find the blocks that correspond to that loop
        - sort those blocks into a good execution order
        - find the loop code for those block with the appropriate loop variable

        This code is intended to work with get_python_loop_code and
        get_python_secondary_loop_code.  It may work with other
        methods.
        """
        if type(indent) == int:
            indent = " "*indent
        loop_blocks = self.get_loop_blocks(loop_num)
        print("loop_num: %s" % loop_num)
        print("loop_blocks:")
        print_block_names(loop_blocks)
        exec_order = self.find_execution_order(block_list=loop_blocks, loop_num=loop_num)
        kwargs = {'istr':loop_var}
        mylist = self.get_code_from_blocks_one_method(method_name, \
                                                      indent=indent, \
                                                      block_list=exec_order, **kwargs)
        return mylist


    def get_python_loop_code_one_loop(self, loop_num=1, loop_var='i', indent="    "):
        return self.get_python_code_one_loop(method_name="get_python_loop_code", \
                                             loop_num=loop_num, loop_var=loop_var, \
                                             indent=indent)


    def get_python_loop1_code(self, **kwargs):
        return self.get_python_loop_code_one_loop(loop_num=1, loop_var='i', **kwargs)


    def get_python_loop2_code(self, **kwargs):
        return self.get_python_loop_code_one_loop(loop_num=2, loop_var='j', **kwargs)


    def get_python_loop3_code(self, **kwargs):
        return self.get_python_loop_code_one_loop(loop_num=3, loop_var='k', **kwargs)



    def get_python_secondary_loop1_code(self, **kwargs):
        return self.get_python_secondary_loop_code_one_loop(loop_num=1, loop_var='i', **kwargs)


    def get_python_secondary_loop2_code(self, **kwargs):
        return self.get_python_secondary_loop_code_one_loop(loop_num=2, loop_var='j', **kwargs)


    def get_python_secondary_loop3_code(self, **kwargs):
        return self.get_python_secondary_loop_code_one_loop(loop_num=3, loop_var='k', **kwargs)


    def generate_python_code(self, output_name, \
                             template_path, \
                             output_folder='', \
                             N=1000, \
                             micropyprint=True):
        """Read in the Python template file and replace various
        strings with the associated lines for the block diagram system
        (sysprecode, blockinitcode, blocksecondaryinitcode, sysinitcode, loopcode, ...)"""
        # Approach for two frequency loops:
        # - check to see if the blocks have loops
        #     - if any block has a loop number, they must all have loop numbers
        #         - all or none
        # - if we are in multi-loop mode, some methods need to be different
        #   and handle the loop #'s
        #     - if there are multiple loops:
        #         - each loop has its own N for blockinitcode
        #         - the N value will be set by sysprecode
        #         - setting the inputs should be unaffected
        #             - I believe this is blocksecondaryinitcode
        #         - pythonloopcode and pythonsecondaryloopcode will be affected
        #         - printing and plotting may be affected, but this will be
        #           handled later

        # check to see if the blocks are assigned to different loops:
        self.check_for_loops()#<-- this sets the variable self.has_loops

        # how do I handle execution order for mulitple loops?
        if not self.has_loops:
            self.find_execution_order()

        self.N = N
        self.python_file = txt_mixin.txt_file_with_list(template_path)

        #self.has_loops

        # if we have loops, tup_list needs to change
        # - "pythonloop1code" or "pythonsecondaryloop1code" need code from
        #   loop 1 blocks and so on for each block

        tup_list = [("sysprecode", self.get_python_pre_code), \
                    ("blockinitcode", self.get_block_python_init_code), \
                    ("blocksecondaryinitcode", self.get_block_secondary_init_code), \
                    ]

        if self.has_loops:
            # each loop has its own code for pythonloop1code, pythonloop2code, ...
            tup_list2 = []

            for i in range(1, self.max_loops+1):
                mystrA = "pythonloop%icode" % i
                myfuncA_attr = "get_python_loop%i_code" % i
                myfuncA = getattr(self, myfuncA_attr)
                tup_list2.append((mystrA, myfuncA))
                mystrB = "pythonsecondaryloop%icode" % i
                myfuncB_attr = "get_python_secondary_loop%i_code" % i
                myfuncB = getattr(self, myfuncB_attr)
                tup_list2.append((mystrB, myfuncB))

            ## tup_list2 = [("pythonloop1code", self.get_python_loop1_code), \
            ##              ("pythonloop2code", self.get_python_loop2_code), \
            ##              ("pythonloop3code", self.get_python_loop3_code), \
            ##              ("pythonsecondaryloop1code", self.get_python_secondary_loop1_code), \
            ##              ("pythonsecondaryloop2code", self.get_python_secondary_loop2_code), \
            ##              ("pythonsecondaryloop3code", self.get_python_secondary_loop3_code), \
            ##              ]

        else:
            tup_list2 = [("pythonloopcode", self.get_python_loop_code), \
                         ("pythonsecondaryloopcode", self.get_python_secondary_loop_code), \
                         ]

        tup_list3 = [("plottingcode", self.get_python_plotting_code), \
                    #("bdsysloopcode", self.get_arduino_loop_code), \
                    #("bdsysprintcode", self.get_arduino_print_code), \
                    #("bdsyswelcomecode", self.get_arduino_welcome_code), \
                    ]

        tup_list += tup_list2 + tup_list3

        if micropyprint:
            tup_list.append(("printingcode", self.gen_micropython_printing_code))

        mylist = self.python_file.list

        # this part could be the same for python and C
        for search_str, method in tup_list:
            ind = mylist.find(search_str)#<-- what to do if search_str isn't found?
            if ind:
                # we need to auto-detect proper indent here
                myline = mylist[ind]
                pound_index = myline.find("#")
                indent = " "*pound_index
                new_ind = ind+1
                mylist.insert(new_ind,"")
                new_code = method(indent=indent)
                mylist[new_ind:new_ind] = new_code
            else:
                print("search_str not found: %s" % search_str)


        # this part also looks very similar to C code saving
        # save:
        curdir = os.getcwd()
        if output_folder:
            os.chdir(output_folder)

        fno, ext = os.path.splitext(output_name)
        outpath = os.path.join(fno + '.py')
        self.python_file.save(outpath)

        os.chdir(curdir)



    def save_model_to_csv(self, filename):
        mylist = []
        self.update_block_list()

        out = mylist.append
        # actuators
        out(["actuators"])
        for actuator_name in self.actuator_name_list:
            actuator = self.actuators_dict[actuator_name]
            cur_list = actuator.get_csv_list_for_row()
            out(cur_list)

        out("")
        # sensors
        out(["sensors"])
        print("sssssssssssssssss")
        print('\n'*3)
        print("sensors:")
        for sensor_name in self.sensor_name_list:
            sensor = self.sensors_dict[sensor_name]
            cur_list = sensor.get_csv_list_for_row()
            print("cur_list: %s" % cur_list)
            out(cur_list)

        out("")
        # blocks
        out(["blocks"])
        out(csv_labels)
        for block in self.get_block_list():
            currow = block.get_csv_list_for_row()
            mylist.append(currow)

        if hasattr(self, "print_blocks"):
            pb_name_list = [block.variable_name for block in self.print_blocks]
            out("")
            out(["print blocks"])
            pb_str = ",".join(pb_name_list)
            out([pb_str])


        if hasattr(self, "menu_param_list"):
            out("")
            out(["menu_params"])
            for row in self.menu_param_list:
                out_str = "%s, %i" % row#menu param str, int for int_only
                                        #(not a float)
                out([out_str])

        # will need to adjust here, because actuators and sensors will
        # have different numbers of entries
        txt_mixin.dump_delimited(filename, mylist, delim=',')


# mostly for use in a gui
input_key = 'input'
output_key = 'output'
math_and_logic_key = 'math and logic'
plant_key = 'plant'
controller_key = 'controller'

#block_categories = [input_key, output_key, math_and_logic_key, plant_key, controller_key]
block_categories = [input_key, math_and_logic_key, plant_key, controller_key]
# the output blocks have caused issues in the past and I am just not doing them
# - at least for now



input_blocks = ['step_input','pulse_input', \
                'int_constant_block', \
                'fixed_sine_input','swept_sine_input', \
                'sloped_step', \
                'float_constant_block', \
                ]

output_blocks = ['output_block']

math_and_logic_blocks = ['addition_block','subtraction_block', \
                         'greater_than_block', 'less_than_block', \
                         'saturation_block', \
                         'sat2_adjustable_block', \
                         'summing_junction','loop_count_block', \
                         'if_block', \
                         'and_block','or_block', \
                         'switch_block', \
                         'abs_block', \
                         'prev_hold_block']

plant_blocks = ['plant','i2c_plant','plant_no_actuator','plant_with_double_actuator', \
                'plant_with_double_actuator_two_sensors', 'cart_pendulum']

controller_blocks = ['P_controller','PD_controller','PI_controller', \
                     'PID_controller','digcomp_block']

block_category_dict = {input_key:input_blocks, \
                       output_key:output_blocks, \
                       math_and_logic_key:math_and_logic_blocks, \
                       plant_key:plant_blocks, \
                       controller_key:controller_blocks, \
                       }



def create_block(block_class, block_type, block_name, **kwargs):
    """block_class must point to a valid class in this module,
    block_type refers to the name of the class, and block_name is the
    name to be associate with the block's variable_name as well as
    added to block_diagram.block_name_list"""
    # - how to handle proper label generation if block_name includes
    #   numbers to put in subscript?
    #     - what kind of blocks get subscripts?
    #         - I am not messing with math or logic blocks
    #
    # Plan:
    # - if block_name ends in numbers, see if block_type contains
    #   input, output, controller, or plant
    p = re.compile("(.*)([0-9]+)")
    print("block_name: %s" % block_name)
    q = p.search(block_name)
    label = None
    if q is not None:
        mykeys = ['input','output','controller','plant']
        found = 0
        for key in mykeys:
            if key in block_type:
                found = 1
                break
        if found:
            label = "$%s_{%s}$" % (q.group(1), q.group(2))

    #print("block_type: %s" % block_type)

    #kwargs = {}
    if label is not None:
        kwargs['label'] = label


    ## input_keys = ['input_block1','input_block2','input_block1_name','input_block2_name']
    ## for key in input_keys:
    ##     if key in kwargs_in:
    ##         kwargs[key] = kwargs_in[key]

    print("in create block, kwargs:")
    print(kwargs)
    myblock = block_class(variable_name=block_name, **kwargs)

    return myblock





class csv_block_diagram_loader(object):
    """A class for loading csv file and converting the rows to a
    block_diagram model.

    The top row of the csv file must contain labels that correspond to
    block attributes, mostly directly naming attributes with a few
    exceptions."""
    # Goal:
    # - read rows from a csv file where the top row is labels and each remaining row
    #   describes one block
    # - output a block_diagram model with the blocks as described
    #     - including setting the inputs and placing the blocks
    #
    # - how does this need to work?
    # - is there a way not to hard code the csv columns?
    # - assume labels in first row
    # - do I want to avoid depending on txt_database?
    #
    # Assumptions:
    # - file is comma delimited
    # - first row contains labels
    # - file is composed of string data (that could be converted to other things)
    #
    # Questions:
    # - is np.loadtxt a good fit?
    # - or am I better off reading a list of lists?
    # - what options are in txt_mixin?
    # - if txt_database is installed with py_block_diagram, why not use it?
    #
    #
    # - is this easier with a csv loader class?
    #     - how to I save the column mapping?
    #     - is there any good reason not to use a class?
    #
    # Approach:
    # - get actuators and sensors
    # - create all blocks:
    #     - need to handle new params
    #     - need to find actuators and sensors for plants
    #     - use the create_block method:
    #         - (block_class, block_type, block_name, **kwargs_in):
    #         - find the block class
    #         - figure out which attrs/columns go in kwargs_in
    #             - width, height, label, .... might not be currently handled by create_block
    #     - which labels/columns are easiest and safe to use for the __init__ method
    # - set the block inputs
    # - place the blocks
    # - check for unused columns

    # find sections and split apart


    # create block_diagram model and append the blocks


    # set the block inputs


    # place the blocks


    # check for unused columns

    def __init__(self, csvpath):
        self.csvpath = csvpath
        self.mod = sys.modules["py_block_diagram"]
        self.init_params = ["variable_name","label","arduino_class", \
                            "width","height"]
        self.input_params = ['input_block1_name','input_block2_name']
        self.abs_params = ['abs_x','abs_y']#just for column mapping check
        self.rel_params = ["rel_pos", "rel_distance", "xshift", "yshift"]
        ## self.init_params = [",variable_name", ",label",, "arduino_class", \
        ##                     "width", "height"]



    def _load_csv(self):
        self.file = txt_mixin.txt_file_with_list(self.csvpath)
        # this approach no longer works:
        # - the file is no longer one uniform spreadsheet section
        ## self.file = txt_mixin.delimited_txt_file(self.csvpath)
        ## self.array = self.file.array
        ## self.labels = self.array[0,:].tolist()
        ## self.block_data = self.array[1:,:]
        ## nvect = np.arange(len(self.labels))
        ## self.column_dict = dict(zip(self.labels,nvect))


    def find_one_column(self, label):
        # should this fail graciously?
        # index = self.labels.index(label)
        index = self.column_dict[label]
        return index


    ##########################################
    #
    # Old Approach
    #
    ##########################################
    # I believe the commented out code below is all from my old
    # approach.  I learned somethings after writing code to
    # read actuators and sensors from csv that cleaned things
    # up a lot.
    ##########################################
    ## def find_columns(self):
    ##     # every entry in csv_labels needs to be handled
    ##     #
    ##     # block_type, ,variable_name, ,label,, arduino_class,
    ##     # input_block1_name, input_block2_name, width, height,
    ##     # placement_type,abs_x, abs_y,
    ##     # rel_block_name, rel_pos, rel_distance, xshift, yshift
    ##     pass

    ## def get_param_one_row(self, row, param):
    ##     float_list = ['width','height','abs_x','abs_y','xshift','yshift','rel_distance']
    ##     myvalue = row[self.column_dict[param]].strip()
    ##     if param in float_list:
    ##         myvalue = float(myvalue)
    ##     return myvalue


    ## def get_class(self, row):
    ##     class_name = self.get_param_one_row(row, 'block_type')
    ##     myclass = getattr(self.mod, class_name)
    ##     return myclass


    ## def get_block_name_from_row(self, row):
    ##     block_name = self.get_param_one_row(row, 'variable_name')
    ##     return block_name


    ## def get_placement_type_one_row(self, row):
    ##     placement_type = self.get_param_one_row(row, 'placement_type')
    ##     return placement_type


    ## def get_row_dict_from_param_list(self, row, param_list):
    ##     # build a dict by finding the columns for each param in
    ##     # param_list, and then getting the values for each column in row
    ##     mydict = {}
    ##     for key in param_list:
    ##         #column = self.column_dict[key]
    ##         #value = row[column]
    ##         value = self.get_param_one_row(row, key)
    ##         mydict[key] = value
    ##     return mydict


    ## def get_block_init_kwargs(self, row):
    ##     mydict = self.get_row_dict_from_param_list(row, self.init_params)
    ##     return mydict


    ## def get_block_input_kwargs(self, row):
    ##     mydict = self.get_row_dict_from_param_list(row, self.input_params)
    ##     return mydict


    ## def get_relative_placement_kwargs_one_row(self, row):
    ##     mydict = self.get_row_dict_from_param_list(row, self.rel_params)
    ##     return mydict


    ## def create_block_from_csv_row(self, row):
    ##     # - row contains on row of an np.ndarray
    ##     # - labels contains the column labels (also as an np.ndarray)
    ##     #
    ##     # Approach:
    ##     # - get the class from block_type
    ##     # - find the __init__ kwargs
    ##     # - call the __init__ method of the class
    ##     curclass = self.get_class(row)
    ##     kwargs = self.get_block_init_kwargs(row)
    ##     print("curclass: %s" % curclass)
    ##     print("kwargs: %s" % kwargs)
    ##     curblock = curclass(**kwargs)
    ##     return curblock


    ## def create_blocks(self):
    ##     # create the blocks:
    ##     # - find the class
    ##     # - build kwargs
    ##     # - call the __init__ method of the class
    ##     block_name_list = []
    ##     block_dict = {}
    ##     for row in self.block_data:
    ##         curblock = self.create_block_from_csv_row(row)
    ##         block_name = curblock.variable_name
    ##         block_name_list.append(block_name)
    ##         block_dict[block_name] = curblock

    ##     self.block_name_list = block_name_list
    ##     self.block_dict = block_dict


    def get_block_by_name(self, block_name):
        return self.block_dict[block_name]


    def set_inputs_for_all_blocks(self):
        # at this point, we have a dict of blocks and a list of block names,
        # but the inputs are only in the rows of self.block_data
        #
        # Approach:
        # - if row contains non-empty names for any input variables, set
        #   the inputs for the block that corresponds to the row
        ##########################################
        # Old:
        ##########################################
        ## for row in self.block_data:
        ##     input_kwargs = self.get_block_input_kwargs(row)
        ##     # call the set input method if the csv param is not empty
        ##     # - methods: set_input_block1, set_input_block2
        ##     # - params: 'input_block1_name','input_block2_name'
        ##     for i in range(1,3):
        ##         key = "input_block%i_name" % i
        ##         print("key = %s" % key)
        ##         if key in input_kwargs:
        ##             value = input_kwargs[key].strip()
        ##             print("value = %s" % value)
        ##             if value:
        ##                 method_name = "set_input_block%i" % i
        ##                 block_name = self.get_block_name_from_row(row)
        ##                 print("block_name = %s" % block_name)
        ##                 cur_block = self.get_block_by_name(block_name)
        ##                 myfunc = getattr(cur_block, method_name)
        ##                 input_block = self.get_block_by_name(value)
        ##                 myfunc(input_block)
        ##########################################
        # New Approach:
        #
        # - this should be simpler now
        # - each block already has its input block names saved
        #   as parameters
        # - if the input name is not None or '', find the block
        #   and call the method

        ## Current Issue (11/5/22):
        ##  - this is fully working for if/then blocks
        ##  - this code assume input_blockN_name maps to set_input_blockN
        ##  - I need bool_input_name:set_bool_input
        ##  - I need a dict of attr names and set function names
        max_N = 6
        attr_names = ["input_block%i_name" % i for i in range(1,max_N)]
        func_names = ["set_input_block%i" % i for i in range(1,max_N)]
        ## a list of pairs of input block attrs and the corresponding
        ## set function names
        extra_pairs = [("bool_input_name","set_bool_input")]
        for attr, func in extra_pairs:
            attr_names.append(attr)
            func_names.append(func)

        attr_func_dict = dict(zip(attr_names, func_names))


        for block_name, curblock in self.block_dict.items():
            for attr, func_name in attr_func_dict.items():
                #i in [1,2]:
                #attr = "input_block%i_name" % i
                #print("attr: %s" % attr)
                if hasattr(curblock, attr):
                    in_name = getattr(curblock, attr)
                    print("hasattr %s, in_name: %s" % (attr, in_name))
                    if in_name:
                        if in_name in self.block_dict:
                            in_block = self.block_dict[in_name]
                        elif in_name in self.sensors_dict:
                            in_block = self.sensors_dict[in_name]
                        #func_name = "set_input_block%i" % i
                        func = getattr(curblock, func_name)
                        func(in_block)


    ## def place_block_one_row(self, row):
    ##     placement_type = self.get_placement_type_one_row(row)
    ##     block_name = self.get_block_name_from_row(row)
    ##     print("block_name = %s" % block_name)
    ##     cur_block = self.get_block_by_name(block_name)

    ##     if placement_type == 'absolute':
    ##         #place_absolute(self, x, y)
    ##         abs_x = float(self.get_param_one_row(row, 'abs_x'))
    ##         abs_y = float(self.get_param_one_row(row, 'abs_y'))
    ##         cur_block.place_absolute(abs_x, abs_y)
    ##     elif placement_type == 'relative':
    ##         #place_relative(self, rel_block, rel_pos='right', rel_distance=4, xshift=0, yshift=0)
    ##         rel_block_name = self.get_param_one_row(row, 'rel_block_name')
    ##         rel_block = self.get_block_by_name(rel_block_name)
    ##         kwargs = self.get_relative_placement_kwargs_one_row(row)
    ##         cur_block.place_relative(rel_block, **kwargs)
    ##     else:
    ##         if placement_type:
    ##             print("placement_type not understood: %s" % placement_type)

    def place_one_block(self, curblock):
        # I cannot pass this off to the block, because it needs to
        # have its rel_block passed to it if necessary
        if curblock.placement_type == 'absolute':
            curblock.place_absolute()#if x and y are None, read
                                     #from self.abs_x and self.abs_y
        elif curblock.placement_type == 'relative':
            rel_block_name = curblock.rel_block_name
            rel_block = self.get_block_by_name(rel_block_name)
            kwargs = {}
            for key in self.rel_params:
                kwargs[key] = getattr(curblock,key)
            print("kwargs: %s" % kwargs)
            curblock.place_relative(rel_block, **kwargs)
        else:
            pt_str = curblock.placement_type.strip()
            if pt_str:
                raise ValueError("placement type not understood: %s" % pt_str)


    def place_all_blocks(self):
        # This should be way simpler now that each block knows its own
        # position parameters
        #
        # I previously assumed the absolute block would be first in
        # the csv file.  This might not be true.  So, intentionally
        # place the absolution block(s) first.


        # blocks may not be saved in the csv file in a propoer order
        # for relative placement
        #
        # Approach:
        #
        # - place all absolute blocks
        # - keep track of placed blocks
        # - do not place a block until its relative block is in the
        #   placed blocks list

        placed_blocks = []
        relative_blocks = []

        for block_name, curblock in self.block_dict.items():
            if curblock.placement_type == 'absolute':
                curblock.place_absolute()#if x and y are None, read
                placed_blocks.append(block_name)
            else:
                relative_blocks.append(block_name)

        # place relative blocks now that abs blocks are placed
        #
        # iterate so that blocks are only placed when their relative
        # block is in the placed_blocks list

        unplaced_blocks = copy.copy(relative_blocks)

        for i in range(100):
            # this is a limited while(1) loop
            j = 0
            N = len(unplaced_blocks)

            if N == 0:
                break

            while (j < N):
                block_name = unplaced_blocks[j]
                curblock = self.get_block_by_name(block_name)
                print("curblock: %s" % curblock)
                rel_block_name = curblock.rel_block_name
                print("rel_block_name: %s" % rel_block_name)
                if rel_block_name in placed_blocks:
                    # this block is ready to place, because its relative
                    # block has already been placed
                    self.place_one_block(curblock)
                    placed_blocks.append(block_name)
                    unplaced_blocks.remove(block_name)
                    N = len(unplaced_blocks)
                else:
                    # try next block and come back to this one on next for loop pass
                    j += 1

        print("placed_blocks:")
        print_list(placed_blocks)

        if len(unplaced_blocks) != 0:
            print("unplaced_blocks:")
            print_list(unplaced_blocks)


    def break_into_sections(self):
        section_headers = ['actuators','sensors','blocks', \
                           'print blocks','menu_params']

        inds = []

        for header in section_headers:
            pat = "^%s$" % header
            res = self.file.findallre(pat)
            if not res:
                print("did not find a match for %s" % header)
            else:
                assert len(res) == 1, "bad mathch: %s" % res
                inds.append(res[0])


        inds.sort()
        assert inds[0] == 0, "file does not start with a header, first header line: %s" % inds[0]

        prev_ind = 0
        chunks = []

        for ind in inds[1:]:
            #print(ind)
            cur_chunk = copy.copy(self.file.list[prev_ind:ind])
            chunks.append(clean_chunk(cur_chunk))
            prev_ind = ind

        last_chunk = copy.copy(self.file.list[ind:])
        chunks.append(clean_chunk(last_chunk))
        self.chunks = chunks


    def chunks_to_dict(self):
        chunks_dict = {}

        for chunk in self.chunks:
            line0 = chunk.pop(0)
            chunks_dict[line0] = chunk

        self.chunks_dict = chunks_dict


    def get_chunk(self, name):
        if name in self.chunks_dict:
            raw_list = self.chunks_dict[name]
            mylist = list(filter(None, raw_list))
        else:
            mylist = []
        return mylist


    def process_actuators_chunk(self):
        act_chunk = self.get_chunk('actuators')
        if len(act_chunk) == 0:
            act_dict = {}
            act_name_list = []
        else:
            act_dict, act_name_list = process_actuator_or_sensor_chunk(act_chunk)

        self.actuators_dict = act_dict
        self.actuator_name_list = act_name_list


    def process_sensors_chunk(self):
        sensor_chunk = self.get_chunk('sensors')
        if len(sensor_chunk) == 0:
            sensor_dict = {}
            sensor_name_list = []
        else:
            sensor_dict, sensor_name_list = process_actuator_or_sensor_chunk(sensor_chunk)

        print("sensor_dict: %s" % sensor_dict)
        self.sensors_dict = sensor_dict
        self.sensor_name_list = sensor_name_list
        print("sensor_name_list: %s" % sensor_name_list)


    def process_blocks_chunk(self):
        blocks_chunk = self.get_chunk('blocks')

        self.block_name_list = []
        self.block_dict = {}

        if len(blocks_chunk) == 0:
            self.labels = []
            self.block_data = []
            self.block_dict_list_from_csv = []
            return None

        ## The code below should only be executed if there are
        ## non-emtpy lines in blocks_chunk
        self.labels = blocks_chunk.pop(0).split(",")
        self.block_data = copy.copy(blocks_chunk)
        # Approach:
        # - convert each row to a dict
        #     - handle the param%i part correctly
        # - get the block class and pass in the rest of the dict
        #   to create the block
        # - handle actuator and sensor for plants later, along with placement and inputs
        # - create the block_diagram model and finish
        #     - pass actuators, sensors, and blocks to the block_diagram
        #       as dicts and name lists
        mydict_list = []
        for row in self.block_data:
            print("row: %s" % row)
            # I need something better than a pure split here:
            # - do I do some complicated regexp thing, or do I just
            #   check for dangling delimiters and "join with next"
            #   until the [ or { or ( match with ], }, or )?
            raw_list = row.split(",")
            row_list = fix_one_delimiter(raw_list, '[',']')
            print("row_list: %s" % row_list)
            curdict = csv_row_to_dict(row_list, self.labels)
            mydict_list.append(curdict)
        self.block_dict_list_from_csv = mydict_list

        # create blocks from self.block_dict_list_from_csv
        # - get the class from "block_type"
        # - pass rest of dict as **kwargs
        # - store to self.block_dict and self.block_name_list
        for curdict in self.block_dict_list_from_csv:
            kwargs = copy.copy(curdict)
            class_name = kwargs.pop('block_type')
            myclass = block_classes_dict[class_name]
            variable_name = kwargs.pop('variable_name')
            print("%s, %s, kwargs: %s" % (class_name, variable_name, kwargs))
            myinstance = myclass(variable_name=variable_name, **kwargs)
            self.block_dict[variable_name] = myinstance
            self.block_name_list.append(variable_name)


    def process_print_blocks_chunk(self):
        pb_chunk = self.get_chunk('print blocks')
        if len(pb_chunk) == 0:
            self.print_block_names = []
        else:
            assert len(pb_chunk) == 1, "something is wrong with the print blocks chunk:\n%s" % str(pb_chunk)
            self.print_block_names = pb_chunk[0].split(",")


    def process_menu_params_chunk(self):
        mp_chunk = self.get_chunk('menu_params')
        self.menu_param_list = []

        if len(mp_chunk) == 0:
            return self.menu_param_list
        else:
            for line in mp_chunk:
                mystr, myint = process_menu_params_line(line)
                self.menu_param_list.append((mystr, myint))
            return self.menu_param_list


    def get_sensors_and_actuators_for_plants(self):
        for block_name, curblock in self.block_dict.items():
            # - is it a plant?
            # - if so, find its actuator and sensor(s) by name
            sensor_name_list = [('sensor_name','sensor'),('sensor1_name','sensor1'), \
                                ('sensor2_name','sensor2')]
            actuator_name_list = [('actuator_name','actuator')]

            if isinstance(curblock,plant):
                print("found a plant: %s" % block_name)
                for name_attr, act_attr in actuator_name_list:
                    # kind of silly to do this as a list, but trying to be
                    # future proof
                    if hasattr(curblock, name_attr):
                        act_name = getattr(curblock, name_attr)
                        if act_name:
                            actuator = self.actuators_dict[act_name]
                            setattr(curblock, act_attr, actuator)


                for name_attr, sensor_attr in sensor_name_list:
                    # kind of silly to do this as a list, but trying to be
                    # future proof
                    print("searching for %s" % name_attr)
                    if hasattr(curblock, name_attr):
                        print("attr found: %s" % name_attr)
                        sensor_name = getattr(curblock, name_attr)
                        print("sensor_name: %s" % sensor_name)
                        if sensor_name:
                            sensor = self.sensors_dict[sensor_name]
                            print("setting: %s, %s, %s" % (curblock, sensor_attr, sensor))
                            setattr(curblock, sensor_attr, sensor)


    def main(self):
        self._load_csv()
        self.break_into_sections()
        self.chunks_to_dict()
        self.process_actuators_chunk()
        self.process_sensors_chunk()
        self.process_blocks_chunk()
        self.process_print_blocks_chunk()
        self.set_inputs_for_all_blocks()
        self.get_sensors_and_actuators_for_plants()
        self.place_all_blocks()
        self.block_diagram = block_diagram(block_name_list=self.block_name_list, \
                                           block_dict=self.block_dict, \
                                           actuators_dict=self.actuators_dict, \
                                           actuator_name_list=self.actuator_name_list, \
                                           sensors_dict=self.sensors_dict, \
                                           sensor_name_list=self.sensor_name_list, \
                                           )
        self.block_diagram.set_print_blocks_from_names(self.print_block_names)
        mp_list = self.process_menu_params_chunk()
        self.block_diagram.menu_param_list = mp_list
        # handle menu_params here



def load_model_from_csv(csvpath):
    """Load a block_diagram model from a csv file using the
    csv_block_diagram_loader class"""
    myloader = csv_block_diagram_loader(csvpath)
    myloader.main()
    return myloader.block_diagram



def findallsubclasses(baseclass):
    #print("==========")
    #print("baseclass: %s" % baseclass)
    sub_class_list = baseclass.__subclasses__()
    sub_sub_list = []
    #print("sub_class_list: %s" % sub_class_list)
    for sub_c in sub_class_list:
        #print("sub_c: %s" % sub_c)
        new_list = findallsubclasses(sub_c)
        sub_sub_list.extend(new_list)
        #print("sub_sub_list: %s" % sub_sub_list)
    return sub_class_list + sub_sub_list


def get_class_names(class_list):
    mylist = []
    for cls in class_list:
        curname = cls.__name__
        mylist.append(curname)

    return mylist



actuator_classes = findallsubclasses(actuator)
actuator_class_names = get_class_names(actuator_classes)
actuator_classes_dict = dict(zip(actuator_class_names, actuator_classes))

actuator_list = ['i2c_actuator','h_bridge', \
                 'custom_actuator', 'pwm_output']#from running findallsubclasses in jupyter

actuator_params_dict = {'h_bridge':['in1_pin', 'in2_pin', 'pwm_pin'], \
                        'pwm_output':['pwm_pin'], \
                        'custom_actuator':['arduino_class', 'init_params'], \
                        'i2c_actuator':['NUM_BYTES'], \
                        }

i2c_act_default = {'NUM_BYTES':5}

h_bridge_defaults = {'in1_pin':6, \
                     'in2_pin':4, \
                     'pwm_pin':9}

pwm_output_defaults = {'pwm_pin':6}
custom_actuator_defaults = {}
actuator_default_params = {'h_bridge': h_bridge_defaults, \
                           'pwm_output': pwm_output_defaults, \
                           'custom_actuator': custom_actuator_defaults, \
                            'i2c_actuator': i2c_act_default}

#in1_pin=6, in2_pin=4, pwm_pin=9, variable_name='HB_actuator', arduino_class='h_bridge_actuator'
# for rc filter: class pwm_output: pwm_pin=9, variable_name

## class custom_actuator(actuator):
##     """A class for actuators like the DualMax motor driver used on my
##     pendulum/cart systems.  I don't want users of this library to be
##     required to install all Pololu drivers.
##     """
##     def __init__(self, variable_name='myname', arduino_class='myclass', init_params=''):
##         """The Arduino code to create an instance of the sensor will be:

##         myclass myname = myclass(init_params);"""
##         self.variable_name = variable_name
##         self.arduino_class = arduino_class
##         self.init_params = init_params
##         self._arduino_param_str = init_params


sensor_classes = findallsubclasses(sensor)
sensor_class_names = get_class_names(sensor_classes)
sensor_list = ['i2c_sensor','encoder', 'analog_input', 'custom_sensor',
               'accelerometer']
sensor_classes_dict = dict(zip(sensor_class_names,sensor_classes))
sensor_params_dict = {'encoder':['pinA','pinB', \
                                 'interrupt_number','sensitivity'], \
                      'analog_input':['ai_pin'], \
                      'custom_sensor':['arduino_class','init_params'], \
                      'accelerometer':['arduino_class','init_params'], \
                      'i2c_sensor':['NUM_BYTES'], \
                      }

encoder_defaults = {'pinA':2, \
                    'pinB':11, \
                    'interrupt_number':0, \
                    'sensitivity':1, \
                    }

analog_input_defaults = {'ai_pin':"A0"}
custom_sensor_defaults = {}
i2c_sens_defaults = {'NUM_BYTES':6}
accel_defaults = {'arduino_class':'azaccel6050', \
                  'init_params':"&accelgyro"}

sensor_default_params = {'encoder': encoder_defaults, \
                         'analog_input': analog_input_defaults, \
                         'custom_sensor': custom_sensor_defaults, \
                         'i2c_sensor': i2c_sens_defaults, \
                         'accelerometer':accel_defaults}





actuator_and_sensor_class_dict = copy.copy(actuator_classes_dict)
actuator_and_sensor_class_dict.update(sensor_classes_dict)

plant_classes = [plant] + findallsubclasses(plant)
plant_class_names = get_class_names(plant_classes)
plants_with_no_actuators_names = ['plant_no_actuator', \
                                  'plant_with_two_i2c_inputs_and_two_i2c_sensors', \
                                  'cart_pendulum']

plants_with_two_sensors_names = ['plant_with_double_actuator_two_sensors',
                                 'plant_with_two_i2c_inputs_and_two_i2c_sensors', \
                                 'cart_pendulum']

block_classes = findallsubclasses(block)
block_class_names = get_class_names(block_classes)
block_classes_dict = dict(zip(block_class_names, block_classes))

# encoder: pinB=11, interrupt_number=0, variable_name='encoder_sensor', arduino_class='encoder'):
## class analog_input(sensor):
##     def __init__(self, ai_pin="A0", \
##                  variable_name='ai_sensor', arduino_class='analog_sensor'):

## class custom_sensor(sensor):
##     """A class for sensors such as the accel z channel of an MPU6050
##     where the sensor class if written by the user or included in the
##     .ino file via a template or something.  This is done so that the
##     Arduino rtblockdiagram method does not depend on libraries like
##     MPU6050.  I don't want potential users of my rtblockdiagram
##     library to have to install many sensor libraries before being able
##     to use my code."""
##     def __init__(self, variable_name='myname', arduino_class='myclass', init_params=''):
##         """The Arduino code to create an instance of the sensor will be:

