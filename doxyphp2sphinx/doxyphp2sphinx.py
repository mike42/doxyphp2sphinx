#!/usr/bin/env python3
"""
This script converts the doxygen XML output, which contains the API description,
and generates reStructuredText suitable for rendering with the sphinx PHP
domain.
"""

from collections import OrderedDict
import xml.etree.ElementTree as ET
import argparse
import os


def render_namespace_by_name(tree, namespace_name):
    root = tree.getroot()
    for child in root:
        if child.attrib['kind'] != 'namespace':
            # Skip non-namespace
            continue
        this_namespace_name = child.find('name').text
        if this_namespace_name != namespace_name:
            continue
        render_namespace_by_ref_id(child.attrib['refid'], this_namespace_name)


def render_namespace_by_ref_id(namespace_ref_id, name):
    print("Processing namespace " + name)
    print("  refid is " + namespace_ref_id)
    prefix = rootNamespace + "::"
    is_root = False
    if name == rootNamespace:
        is_root = True
    elif not name.startswith(prefix):
        print("  Skipping, not under " + rootNamespace)
        return
    xml_filename = inpDir + '/' + namespace_ref_id + '.xml'
    print("  Opening " + xml_filename)
    ns = ET.parse(xml_filename)
    compound = ns.getroot().find('compounddef')
    # Generate some markup
    title = "API documentation" if is_root else name[len(prefix):] + " namespace"

    parts = name[len(prefix):].split("::")
    shortname_idx = "api" if is_root else ("api/" + "/".join(parts[:-1] + ['_' + parts[-1]]).lower())
    shortname_dir = "api" if is_root else ("api/" + "/".join(parts[:-1] + [parts[-1]]).lower())
    glob = "api/*" if is_root else parts[-1].lower() + "/*"
    outfile = outDir + "/" + shortname_idx + ".rst"
    if not os.path.exists(outDir + '/' + shortname_dir):
        os.mkdir(outDir + "/" + shortname_dir)

    print("  Page title will be '" + title + "'")
    print("  Page path will be  '" + outfile + "'")

    # TODO extract description of namespace from comments
    desc = compound.find('detaileddescription').text
    print("  Desc is ... '" + desc  + "'")

    with open(outfile, 'w') as nsOut:
        nsOut.write(title + "\n");
        nsOut.write("=" * len(title) + "\n")
        nsOut.write("""\n.. toctree::
   :glob:

   """ + glob + "\n\n" + desc + "\n")

    for node in compound.iter('innerclass'):
        cl_id = node.attrib['refid']
        cl_name = node.text
        render_class_by_ref_id(cl_id, cl_name)

    for node in compound.iter('innernamespace'):
        ns_id = node.attrib['refid']
        ns_name = node.text
        render_namespace_by_ref_id(ns_id, ns_name)


# Walk the XML and extract all members of the given 'kind'
def class_member_list(compounddef, member_kind):
    res = class_member_dict(compounddef, member_kind)
    return OrderedDict(sorted(res.items())).values()
    

def class_member_dict(compounddef, member_kind):
    # Find items declared on this class
    ret = OrderedDict()
    for section in compounddef.iter('sectiondef'):
        kind = section.attrib['kind']
        if kind != member_kind:
            continue
        for member in section.iter('memberdef'):
            method_name = member.find('definition').text.split("::")[-1]
            ret[method_name] = member
    # Follow-up with items from base classes
    if ("private" in member_kind) or ("static" in member_kind):
        # Private methods are not accessible, and static methods should be
        # called on the class which defines them.
        return ret
    for base_class in compounddef.iter('basecompoundref'):
        # TODO load XML and recurse
        refid = base_class.attrib['refid']
        base_compound_def = compounddef_by_ref_id(refid)
        inherited = class_member_dict(base_compound_def, member_kind)
        for key, value in inherited.items():
            if key not in ret:
                ret[key] = value
    return ret


def class_xml_to_rst(compounddef, title):
    rst = title + "\n"
    rst += "=" * len(title) + "\n\n"

    # Class description
    detailed_description_xml = compounddef.find('detaileddescription')
    detailed_description_text = paras2rst(detailed_description_xml).strip()
    if detailed_description_text != "":
      rst += detailed_description_text + "\n\n"

    # Look up base classes
    extends = []
    implements = []
    for base_class in compounddef.iter('basecompoundref'):
        baserefid = base_class.attrib['refid']
        base_compound_def = compounddef_by_ref_id(baserefid)
        if base_compound_def.attrib['kind'] == "class":
            extends.append(base_compound_def)
        else:
            implements.append(base_compound_def)

    # TODO a small table.
    #  <compoundname>Mike42::GfxPhp::Codec::GifCodec</compoundname>
    # Namespace
    # Base class
    # All implemented interfaces
    # <basecompoundref refid="interfaceMike42_1_1GfxPhp_1_1Codec_1_1ImageEncoder" prot="public" virt="non-virtual">Mike42\GfxPhp\Codec\ImageEncoder</basecompoundref>
    # All known sub-classes]
    qualified_name = compounddef.find('compoundname').text.replace("::", "\\")
    rst += ":Qualified name: ``" + qualified_name + "``\n"
    if len(extends) > 0:
        extends_links = []
        for base_class in extends:
            base_class_name = base_class.find('compoundname').text.split("::")[-1]
            extends_links.append(":class:`" + base_class_name + "`")
        rst += ":Extends: " + ", ".join(extends_links) + "\n"
    if len(implements) > 0:
        implements_links = []
        for base_interface in implements:
            base_interface_name = base_interface.find('compoundname').text.split("::")[-1]
            implements_links.append(":interface:`" + base_interface_name + "`")
        rst += ":Implements: " + ", ".join(implements_links) + "\n"
    rst += "\n"

    # Class name
    if compounddef.attrib['kind'] == "interface":
      rst += ".. php:interface:: " + title + "\n\n" 
    else:
      rst += ".. php:class:: " + title + "\n\n"

    # Methods
    methods = class_member_list(compounddef, 'public-func')
    print("  methods:")
    for method in methods:
        rst += method_xml_to_rst(method, 'method')

    # Static methods
    methods = class_member_list(compounddef, 'public-static-func')
    print("  static methods:")
    for method in methods:
        rst += method_xml_to_rst(method, 'staticmethod')

    return rst


def method_xml_to_rst(member, method_type):
    rst = ""
    documented_params = {}
    dd = member.find('detaileddescription')
    return_info = ret_info(dd)
    params = dd.find('*/parameterlist')
    if params != None:
        # Use documented param list if present
        for arg in params.iter('parameteritem'):
            argname = arg.find('parameternamelist')
            argname_type = argname.find('parametertype').text
            argname_name = argname.find('parametername').text
            argdesc = arg.find('parameterdescription')
            argdesc_para = argdesc.iter('para')
            doco = ("    :param " + argname_type).rstrip() + " " + argname_name + ":\n"
            if argdesc_para != None:
              doco += paras2rst(argdesc_para, "      ")
            documented_params[argname_name] = doco
    method_name = member.find('definition').text.split("::")[-1]
    args_string = method_args_string(member)

    if return_info != None and return_info['returnType'] != None:
      args_string += " -> " + return_info['returnType']
    rst += "  .. php:" + method_type + ":: " + method_name + " " + args_string + "\n\n"
    # Member description
    m_detailed_description_text = paras2rst(dd).strip()
    if m_detailed_description_text != "":
      rst += "    " + m_detailed_description_text + "\n\n"

    # Param list from the definition in the code and use
    # documentation where available, auto-fill where not.
    params = member.iter('param')
    if params != None:
      for arg in params:
        param_key = arg.find('declname').text
        param_defval = arg.find('defval')
        if param_key in documented_params:
          param_doc = documented_params[param_key].rstrip()
          # Append a "." if the documentation does not end with one, AND we
          # need to write about the default value later.
          if param_doc[-1] != "." and param_doc[-1] != ":" and param_defval != None:
            param_doc += "."
          rst += param_doc + "\n"
        else:
          # Undocumented param
          param_name = param_key
          type_el = arg.find('type')
          type_str = "" if type_el == None else para2rst(type_el)
          rst += "    :param " + (unencapsulate(type_str) + " " + param_name).strip() + ":\n"
        # Default value description
        if param_defval != None:
          rst += "      Default: ``" + param_defval.text + "``\n"
    # Return value
    if return_info != None:
        if return_info['returnType'] != None:
            rst += "    :returns: " + itsatype(return_info['returnType'], False) + " -- " + return_info['returnDesc'] + "\n"
        else:
            rst += "    :returns: " + return_info['returnDesc'] + "\n"
    if (params != None) or (return_info != None):
        rst += "\n"
    print("    " +  method_name + " " + args_string)
    return rst


def method_args_string(member):
    params = member.iter('param')
    if params == None:
        # Main option is to use arg list from doxygen
        arg_list = member.find('argsstring').text
        return "()" if arg_list == None else arg_list
    required_param_part = []
    optional_param_part = []
    optional_switch = False
    for param in params:
        param_name = param.find('declname').text
        type_el = param.find('type')
        type_str = "" if type_el == None else para2rst(type_el)
        type_str = unencapsulate(type_str)
        param_str = (type_str + " " + param_name).strip()
        if param.find('defval') != None:
            optional_switch = True
        if optional_switch:
            optional_param_part.append(param_str)
        else:
            required_param_part.append(param_str)
    # Output arg list as string according to sphinxcontrib-phpdomain format
    if len(required_param_part) > 0:
        if len(optional_param_part) > 0:
            # Both required and optional args
            return "(" + ", ".join(required_param_part) + "[, " + ", ".join(optional_param_part) + "])"
        else:
            # Only required args
            return "(" + ", ".join(required_param_part) + ")"
    else:
        if len(optional_param_part) > 0:
            # Only optional args
            return "([" + ", ".join(required_param_part) + "])"
        else:
            # Empty arg list!
            return "()"       


def unencapsulate(typeStr):
    # TODO extract type w/o RST wrapping
    if typeStr[0:8] == ":class:`":
        return (typeStr[8:])[:-1]
    return typeStr


def all_primitives():
    # Scalar type keywords and things you find in documentation (eg. 'mixed')
    # http://php.net/manual/en/functions.arguments.php#functions.arguments.type-declaration
    return ["self", "bool", "callable", "iterable", "mixed", "int", "string", "array", "float", "double", "number"]


def ret_info(dd):
    ret = dd.find('*/simplesect')
    if ret == None:
        return None
    paras = ret.iter('para')
    desc = paras2rst(paras).strip()
    desc_part = (desc + " ").split(" ")
    if desc_part[0] in all_primitives() or desc_part[0][0:8] == ":class:`":
        return {'returnType': unencapsulate(desc_part[0]), 'returnDesc': " ".join(desc_part[1:]).strip()}
    # No discernable return type
    return {'returnType': None, 'returnDesc': desc}


def paras2rst(paras, prefix = ""):
    return "\n".join([prefix + para2rst(x) for x in paras])


def xmldebug(inp):
    print(ET.tostring(inp, encoding='utf8', method='xml').decode())


def para2rst(inp):
    ret = "" if inp.text == None else inp.text
    for subtag in inp:
        txt = subtag.text
        if subtag.tag == "parameterlist":
            continue
        if subtag.tag == "simplesect":
            continue
        if txt == None:
            continue
        if subtag.tag == "ref":
            txt = ":class:`" + txt + "`"
        ret += txt + ("" if subtag.tail == None else subtag.tail)
    return ret


def itsatype(inp, primitives_as_literals = False):
    if inp == None:
        return ""
    if inp == "":
        return ""
    if inp in all_primitives():
        if primitives_as_literals:
          return "``" + inp + "``"
        else:
          return inp
    else:
        return ":class:`" + inp + "`"


def compounddef_by_ref_id(class_ref_id):
    xml_filename = inpDir + '/' + class_ref_id + '.xml'
    cl = ET.parse(xml_filename)
    return cl.getroot().find('compounddef')


def render_class_by_ref_id(class_ref_id, name):
    print("Processing class " + name)
    print("  refid is " + class_ref_id)
    compounddef = compounddef_by_ref_id(class_ref_id)
    prefix = rootNamespace + "::"
    parts = name[len(prefix):].split("::")
    shortname = "api/" + "/".join(parts).lower()
    outfile = outDir + "/" + shortname + ".rst"
    title = parts[-1]

    print("  Class title will be '" + title + "'")
    print("  Class path will be  '" + outfile + "'")
    class_rst = class_xml_to_rst(compounddef, title)

    with open(outfile, 'w') as classOut:
      classOut.write(class_rst)


parser = argparse.ArgumentParser(description='Generate Sphinx-ready reStructuredText documentation or your PHP project, using Doxygen XML as an input.')
parser.add_argument('--xml-dir', dest='xml_dir', default='xml')
parser.add_argument('--out-dir', dest='out_dir', default='.')
parser.add_argument('root_namespace')
args = parser.parse_args()

inpDir = args.xml_dir
outDir = args.out_dir
rootNamespace = args.root_namespace

tree = ET.parse(inpDir + '/index.xml')
render_namespace_by_name(tree, rootNamespace)
