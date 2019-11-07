'''
Thanks for Holy Wen from Nokia Siemens Networks to let me use his code
to put the result into xml file that is compatible with cppncss.
Jenkens has plugin for cppncss format result to display the diagram.
'''


def xml_output(result, verbose):
    import xml.dom.minidom

    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "cppncss", None)
    root = doc.documentElement

    processing_instruction = doc.createProcessingInstruction(
        'xml-stylesheet',
        'type="text/xsl" ' +
        'href="https://raw.github.com/terryyin/lizard/master/lizard.xsl"')
    doc.insertBefore(processing_instruction, root)

    root.appendChild(_create_function_measure(doc, result, verbose))
    root.appendChild(_create_file_measure(doc, result))

    return doc.toprettyxml()


def _create_function_measure(doc, result, verbose):
    measure = doc.createElement("measure")
    measure.setAttribute("type", "Function")
    measure.appendChild(_create_labels(doc, ["Nr.", "NCSS", "CCN","Maintainability"]))

    number = 0
    total_func_ncss = 0
    total_func_ccn = 0
    total_func_maintainability_index = 0

    for source_file in result:
        file_name = source_file.filename
        for func in source_file.function_list:
            number += 1
            total_func_ncss += func.nloc
            total_func_ccn += func.cyclomatic_complexity
            total_func_maintainability_index += func.maintainability_index
            measure.appendChild(
                _create_function_item(
                    doc, number, file_name, func, verbose))

        if number != 0:
            measure.appendChild(
                _create_labeled_value_item(
                    doc, 'average', "NCSS", str(total_func_ncss / number)))
            measure.appendChild(
                _create_labeled_value_item(
                    doc, 'average', "CCN", str(total_func_ccn / number)))
            measure.appendChild(
                _create_labeled_value_item(
                    doc, 'average', "Maintainability", str(total_func_maintainability_index / number)))
    return measure


def _create_file_measure(doc, result):
    measure = doc.createElement("measure")
    measure.setAttribute("type", "File")
    measure.appendChild(
        _create_labels(doc, ["Nr.", "NCSS", "CCN", "Maintainability", "Functions"]))

    file_nr = 0
    file_total_ncss = 0
    file_total_ccn = 0
    file_total_funcs = 0
    file_total_maintainability_index = 0

    for source_file in result:
        file_nr += 1
        file_total_ncss += source_file.nloc
        file_total_ccn += source_file.CCN
        file_total_maintainability_index += source_file.maintainability_index
        file_total_funcs += len(source_file.function_list)
        measure.appendChild(
            _create_file_node(doc, source_file, file_nr))

    if file_nr != 0:
        file_summary = [("NCSS", file_total_ncss / file_nr),
                        ("CCN", file_total_ccn / file_nr),
                        ("Maintainability", file_total_maintainability_index / file_nr),
                        ("Functions", file_total_funcs / file_nr)]
        for key, val in file_summary:
            measure.appendChild(
                _create_labeled_value_item(doc, 'average', key, val))

    summary = [("NCSS", file_total_ncss),
               ("CCN", file_total_ccn),
               ("Functions", file_total_funcs)]
    for key, val in summary:
        measure.appendChild(_create_labeled_value_item(doc, 'sum', key, val))
    return measure


def _create_label(doc, name):
    label = doc.createElement("label")
    text1 = doc.createTextNode(name)
    label.appendChild(text1)
    return label


def _create_labels(doc, label_name):
    labels = doc.createElement("labels")
    for label in label_name:
        labels.appendChild(_create_label(doc, label))

    return labels


def _create_function_item(doc, number, file_name, func, verbose):
    item = doc.createElement("item")
    if verbose:
        item.setAttribute(
            "name", "%s at %s:%s" %
            (func.long_name, file_name, func.start_line))
    else:
        item.setAttribute(
            "name", "%s(...) at %s:%s" %
            (func.name, file_name, func.start_line))
    value1 = doc.createElement("value")
    text1 = doc.createTextNode(str(number))
    value1.appendChild(text1)
    item.appendChild(value1)
    value2 = doc.createElement("value")
    text2 = doc.createTextNode(str(func.nloc))
    value2.appendChild(text2)
    item.appendChild(value2)
    value3 = doc.createElement("value")
    text3 = doc.createTextNode(str(func.cyclomatic_complexity))
    value3.appendChild(text3)
    item.appendChild(value3)
    value4 = doc.createElement("value")
    text4 = doc.createTextNode(str(func.maintainability_index))
    value4.appendChild(text4)
    item.appendChild(value4)
    return item


def _create_labeled_value_item(doc, name, label, value):
    average_ncss = doc.createElement(name)
    average_ncss.setAttribute("lable", label)
    average_ncss.setAttribute("value", str(value))
    return average_ncss


def _create_file_node(doc, source_file, file_nr):
    item = doc.createElement("item")
    item.setAttribute("name", source_file.filename)
    value1 = doc.createElement("value")
    text1 = doc.createTextNode(str(file_nr))
    value1.appendChild(text1)
    item.appendChild(value1)
    value2 = doc.createElement("value")
    text2 = doc.createTextNode(str(source_file.nloc))
    value2.appendChild(text2)
    item.appendChild(value2)
    value3 = doc.createElement("value")
    text3 = doc.createTextNode(str(source_file.CCN))
    value3.appendChild(text3)
    item.appendChild(value3)
    value4 = doc.createElement("value")
    text4 = doc.createTextNode(str(source_file.maintainability_index))
    value4.appendChild(text4)
    item.appendChild(value4)
    value5 = doc.createElement("value")
    text5 = doc.createTextNode(str(len(source_file.function_list)))
    value5.appendChild(text5)
    item.appendChild(value5)
    return item
