﻿##
## Licensed to the .NET Foundation under one or more agreements.
## The .NET Foundation licenses this file to you under the MIT license.
## See the LICENSE file in the project root for more information.
##
##  Sample LTTng Instrumentation code that is generated:
##
## HEADER:
## #define GCFinalizersEnd_TRACEPOINT_ARGS \
##TP_ARGS(\
##        const unsigned int ,Count\
##)
##TRACEPOINT_EVENT_CLASS(
##    DotNETRuntime,
##    GCFinalizersEnd,
##    GCFinalizersEnd_TRACEPOINT_ARGS,
##     TP_FIELDS(
##        ctf_integer(unsigned int, Count, Count)
##    )
##)
##
##CPP :
##
##extern "C" BOOL  EventXplatEnabledGCFinalizersEnd(){ return TRUE;}
##extern "C" ULONG  FireEtXplatGCFinalizersEnd(
##                  const unsigned int Count
##)
##{
##  ULONG Error = ERROR_WRITE_FAULT;
##    if (!EventXplatEnabledGCFinalizersEnd()){ return ERROR_SUCCESS;}
##
##
##     tracepoint(
##        DotNETRuntime,
##        GCFinalizersEnd,
##        Count
##        );
##        Error = ERROR_SUCCESS;
##
##return Error;
##}
##
###define GCFinalizersEndT_TRACEPOINT_INSTANCE(name) \
##TRACEPOINT_EVENT_INSTANCE(\
##    DotNETRuntime,\
##    GCFinalizersEnd,\
##    name ,\
##    GCFinalizersEnd_TRACEPOINT_ARGS \
##)
#

import os
from genXplatEventing import *

stdprolog="""
// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

/******************************************************************

DO NOT MODIFY. AUTOGENERATED FILE.
This file is generated using the logic from <root>/src/scripts/genXplatLttng.py

******************************************************************/
"""
stdprolog_cmake="""
#
#
#******************************************************************

#DO NOT MODIFY. AUTOGENERATED FILE.
#This file is generated using the logic from <root>/src/scripts/genXplatLttng.py

#******************************************************************
"""

specialCaseSizes = { "BulkType" : { "Values" : "Values_ElementSize" }, "GCBulkRootCCW" : { "Values" : "Values_ElementSize" }, "GCBulkRCW" : { "Values" : "Values_ElementSize" }, "GCBulkRootStaticVar" : { "Values" : "Values_ElementSize" } }

lttngDataTypeMapping ={
        #constructed types
        "win:null"          :" ",
        "win:Int64"         :"const __int64",
        "win:ULong"         :"const ULONG",
        "win:count"         :"*",
        "win:Struct"        :"const BYTE *",
        #actual spec
        "win:GUID"          :"const int",
        "win:AnsiString"    :"const char*",
        "win:UnicodeString" :"const char*",
        "win:Double"        :"const double",
        "win:Int32"         :"const signed int",
        "win:Boolean"       :"const BOOL",
        "win:UInt64"        :"const unsigned __int64",
        "win:UInt32"        :"const unsigned int",
        "win:UInt16"        :"const unsigned short",
        "win:UInt8"         :"const unsigned char",
        "win:Pointer"       :"const size_t",
        "win:Binary"        :"const BYTE"
        }

ctfDataTypeMapping ={
        #constructed types
        "win:Int64"         :"ctf_integer",
        "win:ULong"         :"ctf_integer",
        "win:count"         :"ctf_sequence",
        "win:Struct"        :"ctf_sequence",
        #actual spec
        "win:GUID"          :"ctf_sequence",
        "win:AnsiString"    :"ctf_string",
        "win:UnicodeString" :"ctf_string",
        "win:Double"        :"ctf_float",
        "win:Int32"         :"ctf_integer",
        "win:Boolean"       :"ctf_integer",
        "win:UInt64"        :"ctf_integer",
        "win:UInt32"        :"ctf_integer",
        "win:UInt16"        :"ctf_integer",
        "win:UInt8"         :"ctf_integer",  #actually a character
        "win:Pointer"       :"ctf_integer",
        "win:Binary"        :"ctf_sequence"
        }

MAX_LTTNG_ARGS = 9

def shouldPackTemplate(template):
    return template.num_params > MAX_LTTNG_ARGS or len(template.structs) > 0 or len(template.arrays) > 0

def generateArgList(template):
    header = "TP_ARGS( \\\n"
    footer = ")\n"

    if "MethodILToNative" in template.name:
        pass

    if shouldPackTemplate(template):
        args  = "        const unsigned int, length, \\\n"
        args += "        const char *, __data__ \\\n"

    else:
        fnSig = template.signature
        args = []
        for params in fnSig.paramlist:
            fnparam     = fnSig.getParam(params)
            wintypeName = fnparam.winType
            typewName   = lttngDataTypeMapping[wintypeName]
            winCount    = fnparam.count
            countw      = lttngDataTypeMapping[winCount]

            arg = "        " + typewName
            if countw != " ":
                arg += countw
            arg += ", " + fnparam.name
            args.append(arg)
        args = ", \\\n".join(args) + " \\\n"

    return header + args + footer


def generateFieldList(template):
    header = "    " + " TP_FIELDS(\n"
    footer = "\n    )\n)\n"
    
    if shouldPackTemplate(template):
        field_list  = "        ctf_integer(ULONG, length, length)\n"
        field_list += "        ctf_sequence(char, __data__, __data__, ULONG, length)"

    else:
        fnSig = template.signature
        field_list = []
        for params in fnSig.paramlist:
            fnparam     = fnSig.getParam(params)
            wintypeName = fnparam.winType
            winCount    = fnparam.count
            countw      = lttngDataTypeMapping[winCount]
            typewName   = lttngDataTypeMapping[wintypeName].replace("const ","")

            field_body  = None
            ctf_type    = None
            varname     = fnparam.name

            if fnparam.prop:
                #this is an explicit struct treat as a sequence
                ctf_type = "ctf_sequence"
                sizeofseq = fnparam.prop
                field_body = ", ".join((typewName, varname, varname, "size_t", sizeofseq))

            else:
                ctf_type = ctfDataTypeMapping[wintypeName]
                if ctf_type == "ctf_string":
                    field_body = ", ".join((varname, varname))

                elif ctf_type == "ctf_integer" or ctf_type == "ctf_float":
                    field_body = ", ".join((typewName, varname, varname))

                elif ctf_type == "ctf_sequence":
                    raise Exception("ctf_sequence needs to have its memory expilicitly laid out")

                else:
                    raise Exception("no such ctf intrinsic called: " +  ctf_type)

            field_list.append("        %s(%s)" % (ctf_type, field_body))

        field_list = "\n".join(field_list)

    return header + field_list + footer

def generateLttngHeader(providerName, allTemplates, eventNodes):
    lTTngHdr = []
    for templateName in allTemplates:
        template = allTemplates[templateName]
        fnSig   = allTemplates[templateName].signature
        
        lTTngHdr.append("\n#define " + templateName + "_TRACEPOINT_ARGS \\\n")

#TP_ARGS
        tp_args = generateArgList(template)
        lTTngHdr.append(tp_args)

#TP_EVENT_CLASS
        lTTngHdr.append("TRACEPOINT_EVENT_CLASS(\n")
        lTTngHdr.append("    " + providerName + ",\n")
        lTTngHdr.append("    " + templateName + ",\n")
        lTTngHdr.append("    " + templateName + "_TRACEPOINT_ARGS,\n")

#TP_FIELDS
        tp_fields = generateFieldList(template)
        lTTngHdr.append(tp_fields)

# Macro for defining event instance
        lTTngHdr.append("\n#define " + templateName)
        lTTngHdr.append("""T_TRACEPOINT_INSTANCE(name) \\
TRACEPOINT_EVENT_INSTANCE(\\
""")
        lTTngHdr.append("    "+providerName + ",\\\n")
        lTTngHdr.append("    " + templateName + ",\\\n")
        lTTngHdr.append("    name ,\\\n")
        lTTngHdr.append("    " + templateName + "_TRACEPOINT_ARGS \\\n)")



#add an empty template node to just specify the event name in the event stream
    lTTngHdr.append("\n\nTRACEPOINT_EVENT_CLASS(\n")
    lTTngHdr.append("    " + providerName + ",\n")
    lTTngHdr.append("    emptyTemplate ,\n")
    lTTngHdr.append("""    TP_ARGS(),
    TP_FIELDS()
)
#define T_TRACEPOINT_INSTANCE(name) \\
TRACEPOINT_EVENT_INSTANCE(\\
""")
    lTTngHdr.append("    " + providerName + ",\\\n")
    lTTngHdr.append("    emptyTemplate,\\\n")

    lTTngHdr.append("""    name ,\\
    TP_ARGS()\\
)""")
#end of empty template
# create the event instance in headers
    lTTngHdr.append("\n")

    for eventNode in eventNodes:
        eventName    = eventNode.getAttribute('symbol');
        templateName = eventNode.getAttribute('template');

        if not eventName :
            raise Exception(eventNode + " event does not have a symbol")
        if not templateName:
            lTTngHdr.append("T_TRACEPOINT_INSTANCE(")
            lTTngHdr.append(eventName +")\n")
            continue

        subevent = templateName.replace(templateName,'')
        lTTngHdr.append(templateName)
        lTTngHdr.append("T_TRACEPOINT_INSTANCE(")
        lTTngHdr.append(eventName + subevent + ")\n")

    lTTngHdr.append("\n#endif /* LTTNG_CORECLR_H")
    lTTngHdr.append(providerName + " */\n")
    lTTngHdr.append("#include <lttng/tracepoint-event.h>")

    return ''.join(lTTngHdr)


def generateMethodBody(template, providerName, eventName):
    #emit code to init variables convert unicode to ansi string
    result = []

    if template is None:
        return "\n    do_tracepoint(%s, %s);\n" % (providerName, eventName)

    fnSig = template.signature
    
    for paramName in fnSig.paramlist:
        fnparam     = fnSig.getParam(paramName)
        paramname   = fnparam.name

        if fnparam.winType == "win:UnicodeString":
            result.append("    INT " + paramname + "_path_size = -1;\n")
            result.append("    PathCharString " + paramname + "_PS;\n")
            result.append("    INT " + paramname + "_full_name_path_size")
            result.append(" = (PAL_wcslen(" + paramname + ") + 1)*sizeof(WCHAR);\n")
            result.append("    CHAR* " + paramname + "_full_name = ")
            result.append(paramname + "_PS.OpenStringBuffer(" + paramname + "_full_name_path_size );\n")
            result.append("    if (" + paramname + "_full_name == NULL )")
            result.append("    { return ERROR_WRITE_FAULT; }\n")

    result.append("\n")

    #emit tracepoints
    fnSig   = template.signature
        
    if not shouldPackTemplate(template):
        linefnbody = ["    do_tracepoint(%s,\n        %s" % (providerName, eventName)]

        for params in fnSig.paramlist:
            fnparam     = fnSig.getParam(params)
            wintypeName = fnparam.winType
            winCount    = fnparam.count
            paramname   = fnparam.name
            ctf_type    = ctfDataTypeMapping.get(winCount)

            line = "        "
            if not ctf_type:
                ctf_type    = ctfDataTypeMapping[wintypeName]

            if ctf_type == "ctf_string" and wintypeName == "win:UnicodeString":
                #emit code to convert unicode to ansi string

                result.append("    " + paramname+ "_path_size = WideCharToMultiByte( CP_ACP, 0, ")
                result.append(paramname + ", -1, ")
                result.append(paramname + "_full_name, ")
                result.append(paramname + "_full_name_path_size, NULL, NULL );\n")

                result.append("    _ASSERTE(" +paramname+ "_path_size < " )
                result.append(paramname + "_full_name_path_size );\n    ")

                result.append(paramname + "_PS.CloseBuffer(" + paramname + "_path_size );\n")
                result.append("    if( " + paramname + "_path_size == 0 ){ return ERROR_INVALID_PARAMETER; }\n")

                line += paramname + "_full_name"
                linefnbody.append(line)
                continue

            elif ctf_type == "ctf_sequence" or wintypeName == "win:Pointer":
                line += "(" + lttngDataTypeMapping[wintypeName]
                if not lttngDataTypeMapping[winCount] == " ":
                    line += lttngDataTypeMapping[winCount]

                line += ") "
                linefnbody.append(line + paramname)

            else:
                linefnbody.append(line + paramname)

        linefnbody = ",\n".join(linefnbody) + ");\n"
        result.append(linefnbody)
        return ''.join(result)

    else:
        header = """
    char stackBuffer[%s];
    char *buffer = stackBuffer;
    int offset = 0;
    int size = %s;
    bool fixedBuffer = true;

    bool success = true;
""" % (template.estimated_size, template.estimated_size)
        footer = """
    if (!fixedBuffer)
        delete[] buffer;
"""

        pack_list = []
        for paramName in fnSig.paramlist:
            parameter = fnSig.getParam(paramName)

            if paramName in template.structs:
                size = "(int)%s_ElementSize * (int)%s" % (paramName, parameter.prop)
                if template.name in specialCaseSizes and paramName in specialCaseSizes[template.name]:
                    size = "(int)(%s)" % specialCaseSizes[template.name][paramName]
                pack_list.append("    success &= WriteToBuffer((const BYTE *)%s, %s, buffer, offset, size, fixedBuffer);" % (paramName, size))
            elif paramName in template.arrays:
                size = "sizeof(%s) * (int)%s" % (lttngDataTypeMapping[parameter.winType], parameter.prop)
                if template.name in specialCaseSizes and paramName in specialCaseSizes[template.name]:
                    size = "(int)(%s)" % specialCaseSizes[template.name][paramName]
                pack_list.append("    success &= WriteToBuffer((const BYTE *)%s, %s, buffer, offset, size, fixedBuffer);" % (paramName, size))
            elif parameter.winType == "win:GUID":
                pack_list.append("    success &= WriteToBuffer(*%s, buffer, offset, size, fixedBuffer);" % (parameter.name,))
            else:
                pack_list.append("    success &= WriteToBuffer(%s, buffer, offset, size, fixedBuffer);" % (parameter.name,))

        code = "\n".join(pack_list) + "\n\n"
        tracepoint = """    if (!success)
    {
        if (!fixedBuffer)
            delete[] buffer;
        return ERROR_WRITE_FAULT;
    }

    do_tracepoint(%s, %s, offset, buffer);\n""" % (providerName, eventName)

        return header + code + tracepoint + footer
                




def generateLttngTpProvider(providerName, eventNodes, allTemplates):
    lTTngImpl = []
    for eventNode in eventNodes:
        eventName    = eventNode.getAttribute('symbol')
        templateName = eventNode.getAttribute('template')
        #generate EventXplatEnabled
        lTTngImpl.append("extern \"C\" BOOL  EventXplatEnabled%s(){ return tracepoint_enabled(%s, %s); }\n\n" % (eventName, providerName, eventName))
        #generate FireEtw functions
        fnptype = []
        linefnptype = []
        fnptype.append("extern \"C\" ULONG  FireEtXplat")
        fnptype.append(eventName)
        fnptype.append("(\n")

        
        if templateName:
            template = allTemplates[templateName]
        else:
            template = None

        if template:
            fnSig   = template.signature
            for paramName in fnSig.paramlist:
                fnparam     = fnSig.getParam(paramName)
                wintypeName = fnparam.winType
                typewName   = palDataTypeMapping[wintypeName]
                winCount    = fnparam.count
                countw      = palDataTypeMapping[winCount]

                if paramName in template.structs:
                    linefnptype.append("%sint %s_ElementSize,\n" % (lindent, paramName))

                linefnptype.append(lindent)
                linefnptype.append(typewName)
                if countw != " ":
                    linefnptype.append(countw)

                linefnptype.append(" ")
                linefnptype.append(fnparam.name)
                linefnptype.append(",\n")

            if len(linefnptype) > 0 :
                del linefnptype[-1]

        fnptype.extend(linefnptype)
        fnptype.append(")\n{\n")
        lTTngImpl.extend(fnptype)

        #start of fn body
        lTTngImpl.append("    if (!EventXplatEnabled%s())\n" % (eventName,))
        lTTngImpl.append("        return ERROR_SUCCESS;\n")

        result = generateMethodBody(template, providerName, eventName)
        lTTngImpl.append(result)

        lTTngImpl.append("\n    return ERROR_SUCCESS;\n}\n\n")

    return ''.join(lTTngImpl)



def generateLttngFiles(etwmanifest,eventprovider_directory):

    eventprovider_directory = eventprovider_directory + "/"
    tree                    = DOM.parse(etwmanifest)

    #keep these relative
    tracepointprovider_directory =  "tracepointprovider"
    lttng_directory              =  "lttng"

    lttngevntprovPre             = lttng_directory + "/eventprov"
    lttngevntprovTpPre           = lttng_directory + "/traceptprov"

    if not os.path.exists(eventprovider_directory):
        os.makedirs(eventprovider_directory)

    if not os.path.exists(eventprovider_directory + lttng_directory):
        os.makedirs(eventprovider_directory + lttng_directory)

    if not os.path.exists(eventprovider_directory + tracepointprovider_directory):
        os.makedirs(eventprovider_directory + tracepointprovider_directory)

#Top level Cmake
    with open(eventprovider_directory + "CMakeLists.txt", 'w') as topCmake:
        topCmake.write(stdprolog_cmake + "\n")
        topCmake.write("""cmake_minimum_required(VERSION 2.8.12.2)

        project(eventprovider)

        set(CMAKE_INCLUDE_CURRENT_DIR ON)

        add_definitions(-DPAL_STDCPP_COMPAT=1)
        include_directories(${COREPAL_SOURCE_DIR}/inc/rt)
        include_directories(lttng)

        add_library(eventprovider
            STATIC
    """)

        for providerNode in tree.getElementsByTagName('provider'):
            providerName = providerNode.getAttribute('name')
            providerName = providerName.replace("Windows-",'')
            providerName = providerName.replace("Microsoft-",'')

            providerName_File = providerName.replace('-','')
            providerName_File = providerName_File.lower()

            topCmake.write('        "%s%s.cpp"\n' % (lttngevntprovPre, providerName_File))
        
        topCmake.write('        "%shelpers.cpp"\n' % (lttngevntprovPre,))
        topCmake.write(""")
        add_subdirectory(tracepointprovider)

        # Install the static eventprovider library
        install(TARGETS eventprovider DESTINATION lib)
        """)

#TracepointProvider  Cmake

    with open(eventprovider_directory + tracepointprovider_directory + "/CMakeLists.txt", 'w') as tracepointprovider_Cmake:
        tracepointprovider_Cmake.write(stdprolog_cmake + "\n")
        tracepointprovider_Cmake.write("""cmake_minimum_required(VERSION 2.8.12.2)

        project(coreclrtraceptprovider)

        set(CMAKE_INCLUDE_CURRENT_DIR ON)

        add_definitions(-DPAL_STDCPP_COMPAT=1)
        include_directories(${COREPAL_SOURCE_DIR}/inc/rt)
        include_directories(../lttng/)
        add_compile_options(-fPIC)

        add_library(coreclrtraceptprovider
            SHARED
        """)

        for providerNode in tree.getElementsByTagName('provider'):
            providerName = providerNode.getAttribute('name')
            providerName = providerName.replace("Windows-",'')
            providerName = providerName.replace("Microsoft-",'')

            providerName_File = providerName.replace('-','')
            providerName_File = providerName_File.lower()

            tracepointprovider_Cmake.write('        "../'+ lttngevntprovTpPre + providerName_File +".cpp" + '"\n')

        tracepointprovider_Cmake.write("""    )

        target_link_libraries(coreclrtraceptprovider
                              -llttng-ust
        )

        # Install the static coreclrtraceptprovider library
        install_clr(coreclrtraceptprovider)
       """)

    with open(eventprovider_directory + lttng_directory + "/eventprovhelpers.cpp", 'w') as helper:
        helper.write("""
#include "palrt.h"
#include "pal.h"
#include "stdlib.h"
#include "pal_mstypes.h"
#include "pal_error.h"
#include <new>
#include <memory.h>

bool ResizeBuffer(char *&buffer, int& size, int currLen, int newSize, bool &fixedBuffer)
{
	newSize *= 1.5;
	_ASSERTE(newSize > size); // check for overflow

    if (newSize < 32)
        newSize = 32;

	char *newBuffer = new char[newSize];

	memcpy(newBuffer, buffer, currLen);

	if (!fixedBuffer)
		delete[] buffer;

	buffer = newBuffer;
	size = newSize;
	fixedBuffer = false;

	return true;
}

bool WriteToBuffer(const BYTE *src, int len, char *&buffer, int& offset, int& size, bool &fixedBuffer)
{
    if (!src) return true;
	if (offset + len > size)
	{
		if (!ResizeBuffer(buffer, size, offset, size + len, fixedBuffer))
			return false;
	}

	memcpy(buffer + offset, src, len);
	offset += len;
	return true;
}

bool WriteToBuffer(PCWSTR str, char *&buffer, int& offset, int& size, bool &fixedBuffer)
{
    if (!str) return true;
	int byteCount = (PAL_wcslen(str) + 1) * sizeof(*str);

	if (offset + byteCount > size)
	{
		if (!ResizeBuffer(buffer, size, offset, size + byteCount, fixedBuffer))
			return false;
	}

	memcpy(buffer + offset, str, byteCount);
	offset += byteCount;
	return true;
}

bool WriteToBuffer(const char *str, char *&buffer, int& offset, int& size, bool &fixedBuffer)
{
    if (!str) return true;
	int len = strlen(str) + 1;
	if (offset + len > size)
	{
		if (!ResizeBuffer(buffer, size, offset, size + len, fixedBuffer))
			return false;
	}

	memcpy(buffer + offset, str, len);
	offset += len;
	return true;
}""")

# Generate Lttng specific instrumentation
    for providerNode in tree.getElementsByTagName('provider'):

        providerName = providerNode.getAttribute('name')
        providerName = providerName.replace("Windows-",'')
        providerName = providerName.replace("Microsoft-",'')

        providerName_File = providerName.replace('-','')
        providerName_File = providerName_File.lower()
        providerName      = providerName.replace('-','_')

        lttngevntheadershortname = "tp" + providerName_File +".h";
        lttngevntheader          = eventprovider_directory + "lttng/" + lttngevntheadershortname
        lttngevntprov            = eventprovider_directory + lttngevntprovPre + providerName_File + ".cpp"
        lttngevntprovTp          = eventprovider_directory + lttngevntprovTpPre + providerName_File +".cpp"

        lTTngHdr          = open(lttngevntheader, 'w')
        lTTngImpl         = open(lttngevntprov, 'w')
        lTTngTpImpl       = open(lttngevntprovTp, 'w')

        lTTngHdr.write(stdprolog + "\n")
        lTTngImpl.write(stdprolog + "\n")
        lTTngTpImpl.write(stdprolog + "\n")

        lTTngTpImpl.write("\n#define TRACEPOINT_CREATE_PROBES\n")

        lTTngTpImpl.write("#include \"./"+lttngevntheadershortname + "\"\n")

        lTTngHdr.write("""
#include "palrt.h"
#include "pal.h"

#undef TRACEPOINT_PROVIDER

""")

        lTTngHdr.write("#define TRACEPOINT_PROVIDER " + providerName + "\n")
        lTTngHdr.write("""

#undef TRACEPOINT_INCLUDE
""")

        lTTngHdr.write("#define TRACEPOINT_INCLUDE \"./" + lttngevntheadershortname + "\"\n\n")

        lTTngHdr.write("#if !defined(LTTNG_CORECLR_H" + providerName + ") || defined(TRACEPOINT_HEADER_MULTI_READ)\n\n")
        lTTngHdr.write("#define LTTNG_CORECLR_H" + providerName + "\n")

        lTTngHdr.write("\n#include <lttng/tracepoint.h>\n\n")

        lTTngImpl.write("""
#define TRACEPOINT_DEFINE
#define TRACEPOINT_PROBE_DYNAMIC_LINKAGE

#include "stdlib.h"
#include "pal_mstypes.h"
#include "pal_error.h"
#include "pal.h"
#define PAL_free free
#define PAL_realloc realloc
#include "pal/stackstring.hpp"
""")
        lTTngImpl.write("#include \"" + lttngevntheadershortname + "\"\n\n")

        lTTngImpl.write("""#ifndef tracepoint_enabled
#define tracepoint_enabled(provider, name) TRUE
#define do_tracepoint tracepoint
#endif


bool ResizeBuffer(char *&buffer, int& size, int currLen, int newSize, bool &fixedBuffer);
bool WriteToBuffer(PCWSTR str, char *&buffer, int& offset, int& size, bool &fixedBuffer);
bool WriteToBuffer(const char *str, char *&buffer, int& offset, int& size, bool &fixedBuffer);
bool WriteToBuffer(const BYTE *src, int len, char *&buffer, int& offset, int& size, bool &fixedBuffer);

template <typename T>
bool WriteToBuffer(const T &value, char *&buffer, int& offset, int& size, bool &fixedBuffer)
{
	if (sizeof(T) + offset > size)
	{
		if (!ResizeBuffer(buffer, size, offset, size + sizeof(T), fixedBuffer))
			return false;
	}

	*(T *)(buffer + offset) = value;
	offset += sizeof(T);
	return true;
}

""")

        templateNodes = providerNode.getElementsByTagName('template')
        eventNodes = providerNode.getElementsByTagName('event')

        allTemplates  = parseTemplateNodes(templateNodes)
        #generate the header
        lTTngHdr.write(generateLttngHeader(providerName,allTemplates,eventNodes) + "\n")

        #create the implementation of eventing functions : lttngeventprov*.cp
        lTTngImpl.write(generateLttngTpProvider(providerName,eventNodes,allTemplates) + "\n")

        lTTngHdr.close()
        lTTngImpl.close()
        lTTngTpImpl.close()

import argparse
import sys

def main(argv):

    #parse the command line
    parser = argparse.ArgumentParser(description="Generates the Code required to instrument LTTtng logging mechanism")

    required = parser.add_argument_group('required arguments')
    required.add_argument('--man',  type=str, required=True,
                                    help='full path to manifest containig the description of events')
    required.add_argument('--intermediate', type=str, required=True,
                                    help='full path to eventprovider  intermediate directory')
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        print('Unknown argument(s): ', ', '.join(unknown))
        return const.UnknownArguments

    sClrEtwAllMan     = args.man
    intermediate      = args.intermediate

    generateLttngFiles(sClrEtwAllMan,intermediate)

if __name__ == '__main__':
    return_code = main(sys.argv[1:])
    sys.exit(return_code)
