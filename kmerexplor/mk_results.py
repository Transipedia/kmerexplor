#!/usr/bin/env python3
# -*- coding:utf8 -*-


"""
Build results files

- a tabuled file with counts
- a html file to show graphical results (associated with css and javascript files)
"""

import os
import sys
import markdown
import shutil
# ~ import warnings

from counts import Counts


def main():
    """ To test mk_results.py alone """
    class args:
            single = False
            scale = 1
            output = "dev-results"
            method = 'mean'
            config = 'config.yaml'
    counts = Counts(sys.argv[1:], args)
    TSV(counts, args)
    HTML(counts, args)


class TSV:
    """ Class doc """

    def __init__(self, counts, args):
        """ Class initialiser """
        self.tsvfile = counts.to_file(args.output)


class HTML:
    """
    Create all files to show results in HTML page.
    Files created :
    - kmerexplor.html
    - styles.css
    - scripts.js: javacscript code to build graphs
    - echart-en-min.js: echart javascript library
     """

    def __init__(self, counts, args, info, config, tags_file_desc):
        """ Create all html, javascript and css files to show results"""
        self.counts = counts
        self.args = args
        self.scripts_file = 'scripts.js'
        self.htmlfile = os.path.join(args.output, 'kmerexplor.html')
        # ~ self.scale_factor = args.scale
        self.config = config
        self.info = info
        self.tags_file_desc = tags_file_desc
        ### make tree directories
        self.tree_dir = self._mk_tree_dir(args)
        ### Create index.html file
        self._write_index_html(args)
        ### Create styles.css file
        self._write_styles_css()
        ### Create Javascript file for main html page and echarts library
        self._write_scripts_js()
        ### Create Javascript variables for charts
        self._write_variables_js(args)
        ### Create Javascript code to build charts
        self._write_chart_js()
        ### Create Javascript code to add Description (under chart)
        self._write_desc_js()
        ### Create Javascript code to add Home page
        self._write_home_js(args)

    def _mk_tree_dir(self, args):
        """ Function doc """
        tree_dir = os.path.join(args.output, 'lib')
        os.makedirs(tree_dir, exist_ok=True)
        return tree_dir

    def _write_index_html(self, args):
        """ Create index.html page """
        index_html = '<!DOCTYPE html>\n<html>\n'
        index_html += '<head>\n  <meta charset="utf-8" />\n'
        index_html += '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        index_html += '  <link rel="stylesheet" href="lib/styles.css"/>\n'
        index_html += '  <title>{}</title>\n'.format(args.title)
        index_html += '</head>\n'
        ### Side Nav
        index_html += '<body>\n\n<div id="Sidenav" class="sidenav" style="width:250px">\n'
        index_html += '  <a href="#" onclick="home()"><h1>KmerExploR</h1></a>\n'
        index_html += '  <div id=sidenav_items>'
        for metacat in self.config:
            ncategories = 0
            category_html = ''
            for category, conf in self.config[metacat].items():
                if category in self.counts.types:
                    category_html += '    <a href="#" onclick="chartjs(_{})">{}</a>\n'.format(category, conf['sidenav'])
                    ncategories += 1
            if ncategories > 0:
                index_html += '    <div class="meta-category">{}</div>\n'.format(metacat.replace('_', ' '))
                index_html += category_html
        index_html += '  </div>\n'
        index_html += '</div>\n\n'
        ### Main page
        index_html += '<div id="main">\n'
        index_html += '  <div id="header">\n'
        index_html += '    <a href="#" id="hide-icon" onclick="hideElement()">&#9664</a>\n'
        index_html += '    <h1>{}</h1>\n'.format(self.args.title)
        index_html += '  </div>\n'
        index_html += '  <div id=content>\n'
        index_html += '    <div id=home_content></div>\n'
        index_html += '    <div id=chart_content></div>\n'
        index_html += '    <div id=desc_content></div>\n'
        index_html += '  </div>\n'
        index_html += '</div>\n\n'
        index_html += '<script type="text/javascript" src="lib/echarts.common.min.js"></script>\n'
        index_html += '<script type="text/javascript" src="lib/scripts.js"></script>\n'
        index_html += '<script> window.onload = home()</script>\n'
        index_html += '</body>\n'
        index_html += '</html>\n'
        with open(self.htmlfile, 'w') as file:
            file.write(index_html)

    def _write_styles_css(self):
        """ Create css style sheet file """
        styles_css = '@media screen and (max-height: 450px) {.sidenav {padding-top: 15px;}.sidenav a {font-size: 18px;}}'
        styles_css += '* {margin: 0; text-decoration:none;}'
        styles_css += 'p {margin: 8px 0;}'
        styles_css += 'body {font-family: "Lato", sans-serif;}'
        styles_css += '#main {margin-left: 250px;transition: margin-left .5s;}'
        styles_css += '#header {background: #333333;color: #f1f1f1;padding: 4px 8px;}'
        styles_css += '#header h1 {display: inline;margin-left : 8%;}'
        styles_css += '#content {padding: 16px;line-height: 1.5;}'
        ### Table of fastq info
        styles_css += '#fastq-info {text-align: center;border-collapse: collapse;margin-left:20px;}'
        styles_css += '#fastq-info th {background-color:#333333;color: white;}'
        styles_css += '#fastq-info th, #fastq-info td {border: dotted 1px gray;padding: 5px;}'
        styles_css += '#fastq-info > tbody > tr:last-child {font-weight: bold;background-color:lightgrey;}'
        ### Sidenav
        styles_css += '.sidenav {height: 100%;position: fixed;z-index: 1;top: 0;left: 0;background-color: #333333;overflow-x: hidden;transition: 0.5s}'
        styles_css += '#Sidenav h1 {color: #f1f1f1;padding: 8px 10px;}'
        styles_css += '#sidenav_items {padding-top: 30px;}'
        styles_css += '#sidenav_items a {padding: 8px 8px 8px 32px;text-decoration: none;font-size: 20px;color: #8C8C8C;display: block;transition: 0.3s;}'
        styles_css += '#sidenav_items a:hover {color: #f1f1f1;}'
        styles_css += '.meta-category {font-size: 1.2em; padding: 5px 10px; color: #8C8C8C;}'
        styles_css += '#hide-icon {font-size: 30px; color: #8C8C8C;}'
        styles_css += '#hide-icon:hover {color: #f1f1f1;transition: 0.3s}'
        styles_css += 'summary {cursor: pointer;}'
        styles_css += 'hr {margin: 25px 0;}'
        with open(os.path.join(self.tree_dir, 'styles.css'), 'w') as file:
            file.write(styles_css)

    def _write_scripts_js(self):
        """ Create Javascript file """
        ### Refresh charts when chart_content div is resized
        scripts_js = '// These 3 lines aim to refresh chart when the "chart_content" div is resized\n'
        scripts_js += 'var myChart = echarts.init(document.getElementById("chart_content"),);\n'
        scripts_js += 'window.addEventListener("resize", function(event){myChart.resize();});\n'
        scripts_js += 'function resizeChart() {myChart.resize()}\n\n'
        ### Manage sliding sidenav
        scripts_js += '// Manage sliding sidenav\n'
        scripts_js += 'function hideElement() {var x = document.getElementById("Sidenav"); var hideIcon = document.getElementById("hide-icon");if (x.style.width === "0px") {x.style.width = "250px";document.getElementById("main").style.marginLeft = "250px";hideIcon.innerHTML = "&#9664";} else {x.style.width = "0";document.getElementById("main").style.marginLeft= "0";hideIcon.innerHTML = "&#9654";};setTimeout(resizeChart, 500);}\n'
        ### Write as javascript code
        with open(os.path.join(self.tree_dir, self.scripts_file), 'w') as file:
            file.write(scripts_js)
        ### echarts.js Javascript code
        src = f"{os.path.dirname(os.path.realpath( __file__ ))}/echarts.common.min.js"
        dest = os.path.join(self.tree_dir,'echarts.common.min.js')
        shutil.copyfile(src, dest)

    def _write_variables_js(self, args):
        """ Build Javascript code to charts """
        variables_js = ""
        ### firstly, set samples variables
        variables_js += "\n// Samples array variable\n"
        variables_js += "var samples = ['Samples', {}];\n".format(", ".join("'{}'".format(sample) for sample in self.counts.samples))
        variables_js += "var samples_as_fastq = ['Samples', {}];\n".format(", ".join("'{}'".format(sample) for sample in self.counts.fastq))
        ### With the help of config.yaml file, build config variable for each categories
        for metacat in self.config:
            for categ, conf in self.config[metacat].items():
                ### set particular variables
                ## number of seq_id per category
                as_fastq = True if 'as_fastq' in conf else False
                if as_fastq:
                    counts_set = self.counts.get_by_category(categ, mode='single')
                else:
                    counts_set = self.counts.get_by_category(categ)

                if counts_set:
                    ### Organize counts, sorted or percent if define in config.yaml
                    if 'as_percent' in conf:
                        counts_set = set_count_as_percent(counts_set)
                    else:
                        counts_set.sort()
                    nb_categ = nb_legend = len(counts_set)
                    ### special case: category
                    if as_fastq:
                    # ~ if categ == 'Orientation':
                        nb_legend //= 4
                    ## threshold
                    if 'as_percent' not in conf:
                        if isinstance(conf['threshold'], (int, float)):
                            thd = str(conf['threshold'])
                            threshold = "[{yAxis:" + "{},".format(thd) + "}],"
                        elif isinstance(conf['threshold'], str):
                            threshold = "["
                            thresholds = conf['threshold'].split(",")
                            for thd in thresholds:
                                thd = str(float(thd) * args.scale)
                                threshold += "{yAxis:" + thd + "},"
                            threshold += "],"
                        elif not conf['threshold']:
                            threshold = 'false,'
                    else:
                        threshold = 'false,'
                    ## Magical formula to compute height space for legend (depend of number of sequences id)
                    grid_top = 14 + nb_legend * 5 // 11
                    ### Define Dataset
                    lblank = " " * 16
                    dataset = ""
                    if threshold != 'false,':
                        dataset += '{}[],\n'.format(lblank)
                    ## populate Dataset
                    for seq_id in counts_set:
                        gene, counts = seq_id[:]
                        if gene[-4:] == '_rev':
                            dataset += "{}['{}', {}],\n".format(lblank, gene[:-4], ", ".join([str(-count) for count in counts]))
                        else:
                            dataset += "{}['{}', {}],\n".format(lblank, gene, ", ".join([str(count) for count in counts]))
                    ### Define max Y axys
                    yAxys_max = 'null'
                    ### when as_percent is set, Y axys max = 100
                    if 'as_percent' in conf:
                        yAxys_max = '100'
                    elif conf['threshold']:
                            thld = conf['threshold']
                            ### when threshold is single
                            if isinstance(thld, (int, float)):
                                thld = conf['threshold']
                                max_value = 0
                                for counts in counts_set:
                                    ### positives values
                                    if thld > 0:
                                        max_value = max(sum(counts[1]), max_value)
                                    if thld < 0:
                                    ### negatives values
                                        max_value = min(sum(counts[1]), max_value)
                                if thld > max_value:
                                    yAxys_max = str(thld)
                            ### When multiple threshold
                            elif isinstance(conf['threshold'], str):
                                ### yaxis max for mutlitple threshold is not managed at this time.
                                pass

                    ### Define description/explanation of category
                    if conf["desc"]:
                        desc =  '        "' + '",\n        "'.join([line.replace('"',"'") for line in conf["desc"]]) + '"\n'
                    else:
                        desc = ''

                    ### Build Javascript variable code
                    variables_js += "\n// metadata and dataset to build graph\n"
                    variables_js += "var _{} = ".format(categ)
                    variables_js += "{\n"
                    variables_js += "    chart_type: '{}',\n".format(conf['chart_type'])
                    variables_js += "    theme: '{}',\n".format(conf['chart_theme'])
                    variables_js += "    threshold: {}\n".format(threshold)
                    variables_js += "    yAxis_max: {},\n".format(yAxys_max)
                    variables_js += "    toolbox_type: ['stack', 'tiled'],\n"
                    variables_js += '    title_text: "{}",\n'.format(conf['title'])
                    variables_js += '    show_fastq: {},\n'.format('true' if as_fastq else 'false')
                    variables_js += "    legend_padding_top: [40, 30, 0, 30],\n"
                    variables_js += "    grid_top: '{}%',\n".format(grid_top)
                    variables_js += "    nb_seqId: {},\n".format(nb_categ)
                    variables_js += "    dataset: [\n"
                    variables_js += "{}".format(dataset)
                    variables_js += "    ],\n"
                    variables_js += "    desc: [\n"
                    variables_js += "{}".format(desc)
                    variables_js += "    ]\n"
                    variables_js += "};\n\n"

        ### write javascript code
        dest = os.path.join(self.tree_dir, self.scripts_file)
        with open(dest, 'a') as file:
            file.write(variables_js)

    def _write_chart_js(self):
        """
        Build Javascript code to draw charts
        2 functions will be created:
        - set_series(): freezed code, but depanding of number of categories
        - chartjs(): draw chart for one category, using category variable and set_series() function
        """
        ### Create function to set series
        chartjs  = "// Define serie for chartjs() function\n"
        chartjs += "function set_series(category) {\n"
        chartjs += "    if (typeof category.stack == 'undefined') {\n"
        chartjs += "        category.stack = 'one';\n"
        chartjs += "    };\n"
        chartjs += "    /* Build series Object for chartjs() */\n"
        chartjs += "    series = [];\n"
        chartjs += "    if (category.threshold) {\n"
        chartjs += "        series.push({type: 'line', seriesLayoutBy: 'row', markLine: {symbol: 'none', label: {show: true,formatter: 'Threshold'},lineStyle: {width: 2, opacity: 0.6}, data: category.threshold}});\n"
        chartjs += "    };\n"
        chartjs += "    for (i=0, c=category.nb_seqId; i<c; i++) {\n"
        chartjs += "        series.push({type: category.chart_type, stack: category.stack, seriesLayoutBy: 'row'});\n"
        chartjs += "    }\n"
        chartjs += "    return series\n"
        chartjs += "}\n"
        ### Create function to draw chart for one category
        ## define dataZoom
        dataZoom = ''
        minimum_dz = 20
        nb_samples = len(self.counts.samples)
        if nb_samples > minimum_dz:
            # ~ ratio = nb_samples / 100
            # ~ gap = max(minimum_dz // 2 // ratio, 10)
            # ~ mini, maxi = 50-gap, 50+gap
            dataZoom += "                type: 'slider',\n"
            # ~ if nb_samples > 150:
                # ~ dataZoom += "                start: {},\n".format(mini)
                # ~ dataZoom += "                end: {},\n".format(maxi)
            dataZoom += "            },{\n"

        ## Build javascript code
        chartjs += "\n// chartjs() draw chart using values from one category and set_series() function\n"
        chartjs += "function chartjs(category) {\n"
        chartjs += "    // clear home content\n"
        chartjs += "    home_html = document.getElementById('home_content');\n"
        chartjs += "    home_html.innerHTML = '';\n"
        chartjs += "    // weight of chart content\n"
        chartjs += "    chart_html = document.getElementById('chart_content');\n"
        chartjs += "    chart_html.style.height = '600px';\n"
        chartjs += "    // set series (same object * categories count)\n"
        chartjs += "    series = set_series(category);\n"
        chartjs += "    // dataset = samples + dataset\n"
        chartjs += "    if (category.dataset[0][0] != 'Samples') {\n"
        chartjs += "        if (category.show_fastq) {\n"
        chartjs += "            category.dataset.unshift(samples_as_fastq);\n"
        chartjs += "        } else {\n"
        chartjs += "            category.dataset.unshift(samples);\n"
        chartjs += "        };\n"
        chartjs += "    };\n"
        chartjs += "    // clear charts\n"
        chartjs += "    echarts.dispose(document.getElementById('chart_content'));\n"
        chartjs += "    // init chart\n"
        chartjs += "    myChart = echarts.init(\n"
        chartjs += "        document.getElementById('chart_content'),\n"
        chartjs += "        category.theme,\n"
        chartjs += "    );\n"
        chartjs += "    // specify chart configuration item and data\n"
        chartjs += "    var option = {\n"
        chartjs += "        dataset: {\n"
        chartjs += "            source: category.dataset\n"
        chartjs += "        },\n"
        chartjs += "        title: {text: category.title_text},\n"
        chartjs += "        toolbox: {\n"
        chartjs += "            feature: {\n"
        chartjs += "                magicType: {type: category.toolbox_type},\n"
        chartjs += "                dataZoom: {yAxisIndex: false},\n"
        chartjs += "                saveAsImage: {pixelRatio: 2}\n"
        chartjs += "            }\n"
        chartjs += "        },\n"
        chartjs += "        tooltip: {},\n"
        chartjs += "        emphasis: {focus: 'series'},\n"
        chartjs += "        legend: {\n"
        chartjs += "          padding: [40, 30, 0, 30],\n"
        chartjs += "          selector: true,\n"
        chartjs += "        },\n"
        chartjs += "        dataZoom: [{\n"
        chartjs += dataZoom
        chartjs += "                type: 'inside',\n"
        chartjs += "            }],\n"
        chartjs += "        grid: {\n"
        chartjs += "            top: category.grid_top\n"
        chartjs += "        },\n"
        chartjs += "        xAxis: {type: 'category'},\n"
        chartjs += "        yAxis: {\n"
        chartjs += "            name: 'Counts',\n"
        chartjs += "            nameLocation: 'center',\n"
        chartjs += "            nameGap: 80,\n"
        chartjs += "            nameTextStyle: {fontSize: 16,},\n"
        chartjs += "            max: category.yAxis_max,\n"
        chartjs += "        },\n"
        chartjs += "        series: series,\n"
        chartjs += "    };\n"
        chartjs += "    myChart.setOption(option);\n\n"
        chartjs += "    // Add Description;\n"
        chartjs += "    description(category);\n"
        chartjs += "};\n"

        ### write javascript code
        dest = os.path.join(self.tree_dir, self.scripts_file)
        with open(dest, 'a') as file:
            file.write(chartjs)

    def _write_desc_js(self):
        """
        Build code to add description
        """
        descjs = '\n// Set the description of the category in "desc_content" div id\n'
        descjs += 'function description(category) {\n'
        descjs += '    var desc = category.desc;\n'
        descjs += '    desc_html = document.getElementById("desc_content");\n'
        descjs += '    desc_html.innerHTML = "";\n'
        descjs += '    for (i=0; i<desc.length; i++) {\n'
        descjs += '        if (i==0) {\n'
        descjs += '            desc_html.innerHTML += "<h2>" + desc[i] + "</h2>";\n'
        descjs += '        } else {\n'
        descjs += '            desc_html.innerHTML += "<p>" + desc[i] + "</p>";\n'
        descjs += '        }\n'
        descjs += '    }\n'
        descjs += '}\n'

        ### write javascript code
        dest = os.path.join(self.tree_dir, self.scripts_file)
        with open(dest, 'a') as file:
            file.write(descjs)

    def _write_home_js(self, args):
        """
        Build code to add home page
        """
        ### information of analysis (samples, version, etc.)
        msg_info = []
        msg_info.append("<p>Mode: {}</p>".format(self.counts.mode))
        msg_info.append("<p>{} version: {}</p>".format(self.info.APPNAME, self.info.VERSION))
        # ~ if args.scale != 1:
            # ~ msg_info.append("<p>Scale: x{}</p>".format(args.scale))
        msg_info.append("<details><p><summary>{} samples analysed</summary></p>".format(len(self.counts.samples)))
        msg_info.append("<p>{}</p></details>".format(" - ".join(self.counts.samples)))

        ### Information on fastq files
        msg_fastq_info = []
        if self.counts.meta['fastq_files']:
            msg_fastq_info.append("<details><p><summary>About fastq files</summary></p>")
            msg_fastq_info.append("<table id='fastq-info'><tbody>")
            msg_fastq_info.append("<tr><th>Fastq file</th><th>number of kmers</th><th>number of reads</th></tr>")
            for fastq in self.counts.meta['fastq_files'].items():
                msg_fastq_info.append("<tr>"
                                    f"<td>{fastq[0]}</td>"
                                    f"<td>{fastq[1][0]}</td>"
                                    f"<td>{fastq[1][1]}</td>"
                                    "</tr>")
            msg_fastq_info.append("<tr><td>Total</td>"
                                 f"<td>{self.counts.meta['total_kmers']}</td>"
                                 f"<td>{self.counts.meta['total_reads']}</td>"
                                 "</tr>")
            msg_fastq_info.append("</tbody></table>")
            msg_fastq_info.append("</details>")
            # ~ print("fastq files info:", self.counts.meta['fastq_files'])
            # ~ print("read:", self.counts.meta['total_reads'])
            # ~ print("kmers:", self.counts.meta['total_kmers'])


        ### General description of kmerexplor (use markdown file or invite to set it)
        tags_desc = '<h3>Description</h3>'
        if self.tags_file_desc:
            with open(self.tags_file_desc) as f:
                text = f.read()
                tags_desc = markdown.markdown(text, extensions=['attr_list']).replace('\n', '').replace('"', "'")
        else:
            md_file = f"{os.path.splitext(args.setfiles['tags'].split('.gz')[0])[0]}.md"
            tags_desc += (f"<p>You can create a markdown file <strong>{md_file}</strong> "
                           "to describe the tag set. It will be displayed here.</p>")
        # build Javascript code to home page
        homejs = "\n// Home page\n"
        homejs += "function home() {\n"
        homejs += "    // clear home content\n"
        homejs += "    home_html = document.getElementById('home_content');\n"
        homejs += "    home_html.innerHTML = '';\n"
        homejs += "    // clear charts\n"
        homejs += "    chart_html = document.getElementById('chart_content');\n"
        homejs += "    chart_html.innerHTML = '';\n"
        homejs += "    chart_html.style.height = 0;\n"
        homejs += "    // clear chart description\n"
        homejs += "    desc_html = document.getElementById('desc_content');\n"
        homejs += "    desc_html.innerHTML = '';\n"
        homejs += "    // content of Home page\n"
        homejs += '    home_html.innerHTML += "' + ''.join(msg_info) + '";\n'
        homejs += '    home_html.innerHTML += "' + ''.join(msg_fastq_info) + '";\n'
        homejs += "    home_html.innerHTML += '<hr />';\n"
        homejs += f'    home_html.innerHTML += "{tags_desc}";\n'
        homejs += "    };\n"


        ### write javascript code
        dest = os.path.join(self.tree_dir, self.scripts_file)
        with open(dest, 'a') as file:
            file.write(homejs)


def set_count_as_percent(counts_set):
    """ set counts in percentage results """
    new_counts_set = []
    seqid_len = len(counts_set)
    ### convert counts columns as rows and rows as columns
    zipped_counts = list(zip(*[counts_set[i][1] for i in range(seqid_len)]))
    for i in range(seqid_len):
        new_counts = []
        for counts in zipped_counts:
            if sum(counts) != 0:
                ### add percents counts at new_counts
                new_counts.append(round(100 * counts[i] / sum(counts),2))
            else:
                new_counts.append(0)
        ### build new_counts_set with percents counts
        new_counts_set.append((counts_set[i][0], new_counts))
    return new_counts_set


if __name__ == "__main__":
    main()
