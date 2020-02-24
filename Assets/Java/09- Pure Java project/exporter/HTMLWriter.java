package specksboy.exporter;

import java.awt.Desktop;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.DecimalFormat;

import javax.swing.filechooser.FileSystemView;

import specksboy.halstead.metrics.Initiator;
import specksboy.halstead.metrics.MetricsEvaluator;
import specksboy.halstead.metrics.Operands;
import specksboy.halstead.metrics.Operators;

@SuppressWarnings("unused")
public class HTMLWriter {
	public String getName(File file) {
		char[] array = file.getName().toCharArray();
		String temp = "";
		for (int i = 0; i < array.length; i++) {
			if (array[i] == '.') {
				break;
			}
			temp += array[i];
		}
		return temp;
	}

	public double RoundTo2Decimals(double val) {
		DecimalFormat df2 = new DecimalFormat("###.##");
		return Double.valueOf(df2.format(val));
	}

	public boolean export(File file) throws Exception {
		if (file == null) {
			return false;
		} else
			if (file.getName().contains(".java") || file.getName().contains(".cpp") || file.getName().contains(".c")) {
			StringBuffer buffer = new StringBuffer();
			MetricsEvaluator me = new Initiator().initiate(file.getPath());
			File outputFile = new File(file.getParent() + File.separator + getName(file) + ".html");
			BufferedWriter bfw = new BufferedWriter(new FileWriter(outputFile));
			if (!file.exists()) {
				file.createNewFile();
			}

			buffer.append("<!DOCTYPE HTML>" + "<html>" + " <head>" + " <title>Halstead Metrics</title>"
					+ "<style type=\"text/css\">" + "#header{" + "border:2px solid #a1a1a1;" + "padding:10px 40px;"
					+ "background:#dddddd;" + "width:800px;" + "margin-left: 250px;" + "border-radius:25px;" + "}"
					+ "h1{" + "font-family: sans-serif;" + "font-size: 50px;" + "margin-left: 10px;" + "}" + "#body{"
					+ "font-family: sans-serif;" + "border:2px solid #a1a1a1;" + "padding:10px 40px;" + "width:800px;"
					+ "margin-left: 250px;" + "}" + "#footer{" + "border:2px solid #a1a1a1;" + "padding:10px 40px;"
					+ "background:#dddddd;" + "width:800px;" + "margin-left: 250px;" + "border-radius:25px;" + "}"
					+ "#footer-contents{" + "font-family: sans-serif;" + "margin-left: 270px;" + "}" + "table, th, td{"
					+ "border: 2px solid #a1a1a1;" + "}" + "table{" + "border-collapse:collapse;" + "margin-left: 80px;"
					+ "}" + "th,td{" + "text-align: center;" + "padding:5px;" + "}" + "th{" + "background:#dddddd;"
					+ "}" + "</style>" + "</head>");
			buffer.append("<body>" + "<div id=\"layout\">" + "<div id=\"header\">"
					+ "<h1 id=\"heading\">Halstead Metrics Detailed Report</h1>" + "</div>" + "<div id=\"body\">"
					+ "<br /><p><h3>File Name: </h3>" + file.getName() + "</p>");
			buffer.append("<br /><h4><u>Operators</u></h4>" + "<table border=\"1\">" + "<tr>" + "<th>" + "Name"
					+ "</th>" + "<th>" + "Count" + "</th>" + "</tr>");
			for (int i = 0; i < Operators.getInstance().name.size(); i++) {
				buffer.append("<tr>" + "<td>" + Operators.getInstance().name.get(i).toString() + "</td>" + "<td>"
						+ Operators.getInstance().count.get(i).toString() + "</td>" + "</tr>");
			}
			buffer.append("</table>");
			buffer.append("<br /><h4><u>Operands</u></h4>" + "<table border=\"1\">" + "<tr>" + "<th>" + "Name" + "</th>"
					+ "<th>" + "Count" + "</th>" + "</tr>");
			for (int i = 0; i < Operands.getInstance().name.size(); i++) {
				buffer.append("<tr>" + "<td>" + Operands.getInstance().name.get(i).toString() + "</td>" + "<td>"
						+ Operands.getInstance().count.get(i).toString() + "</td>" + "</tr>");
			}

			buffer.append("</table>");

			buffer.append("<br><h4><u>Values</u></h4>" + "<table border=\"1\">" + "<tr>"
					+ "<th>No of Distinct Operators(n1)</th>" + "<td>" + RoundTo2Decimals(me.n1) + "</td>" + "</tr>"
					+ "<tr>" + "<th>No of Distinct Operands(n2)</th>" + "<td>" + RoundTo2Decimals(me.n2) + "</td>"
					+ "</tr>" + "<tr>" + "<th>Total No of Operators(N1)</th>" + "<td>" + RoundTo2Decimals(me.N1)
					+ "</td>" + "</tr>" + "<tr>" + "<th>Toatl No of Operands(N2)</th>" + "<td>"
					+ RoundTo2Decimals(me.N2) + "</td>" + "</tr>" + "<tr>" + "<th>Program Length</th>" + "<td>"
					+ RoundTo2Decimals(me.PROGRAM_LENGTH) + "</td>" + "</tr>" + "<tr>" + "<th>Program Vocabulary</th>"
					+ "<td>" + RoundTo2Decimals(me.PROGRAM_VOCABULARY) + "</td>" + "</tr>" + "<tr>"
					+ "<th>Estimated Length</th>" + "<td>" + RoundTo2Decimals(me.ESTIMATED_LENGTH) + "</td>" + "</tr>"
					+ "<tr>" + "<th>Purity Ratio</th>" + "<td>" + RoundTo2Decimals(me.PURITY_RATIO) + "</td>" + "</tr>"
					+ "<tr>" + "<th>Volume</th>" + "<td>" + RoundTo2Decimals(me.VOLUME) + "</td>" + "</tr>" + "<tr>"
					+ "<th>Difficulty</th>" + "<td>" + RoundTo2Decimals(me.DIFFICULTY) + "</td>" + "</tr>" + "<tr>"
					+ "<th>Program Effort</th>" + "<td>" + RoundTo2Decimals(me.PROGRAM_EFFORT) + "</td>" + "</tr>"
					+ "<tr>" + "<th>Programming Time</th>" + "<td>" + RoundTo2Decimals(me.PROGRAMMING_TIME) + "</td>"
					+ "</tr>" + "</table>");

			buffer.append("</div>" + "<div id=\"footer\">"
					+ "<p id=\"footer-contents\">Copyright &copy; Reserved 2014. <strong>Specksboy</strong> Inc.</p>"
					+ "</div>" + "</div>" + "</body>" + "</html>");
			bfw.write(buffer.toString());
			bfw.close();
			Desktop.getDesktop().open(outputFile);
			return true;
		} else {
			return false;
		}
	}
}
