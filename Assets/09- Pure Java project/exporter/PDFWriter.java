package specksboy.exporter;

import java.awt.Desktop;
import java.io.File;
import java.io.FileOutputStream;
import java.text.DecimalFormat;

import com.itextpdf.text.BaseColor;
import com.itextpdf.text.Document;
import com.itextpdf.text.DocumentException;
import com.itextpdf.text.Element;
import com.itextpdf.text.Font;
import com.itextpdf.text.PageSize;
import com.itextpdf.text.Paragraph;
import com.itextpdf.text.Rectangle;
import com.itextpdf.text.pdf.PdfPCell;
import com.itextpdf.text.pdf.PdfPTable;
import com.itextpdf.text.pdf.PdfWriter;

import specksboy.halstead.metrics.Initiator;
import specksboy.halstead.metrics.MetricsEvaluator;
import specksboy.halstead.metrics.Operands;
import specksboy.halstead.metrics.Operators;

public class PDFWriter {
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
		} else if (file.getName().toLowerCase().contains(".java") || file.getName().toLowerCase().contains(".cpp")
				|| file.getName().toLowerCase().contains(".c")) {
			MetricsEvaluator me = new Initiator().initiate(file.getPath());
			File outputFile = new File(file.getParent() + File.separator + getName(file) + ".pdf");
			if (!file.exists()) {
				file.createNewFile();
			}
			Document document = new Document();
			try {
				PdfWriter writer = PdfWriter.getInstance(document, new FileOutputStream(outputFile));
				document.setPageSize(PageSize.LETTER);
				document.setMargins(36, 72, 108, 180);
				document.setMarginMirroring(false);
				ParagraphBorder border = new ParagraphBorder();
				writer.setPageEvent(border);
				document.open();
				document.addAuthor("Specksboy Inc.");
				document.addCreationDate();
				document.addCreator("Specksboy Inc.");
				document.addTitle("Halstead Metrics - " + getName(file) + " Report");
				document.addProducer();
				document.addSubject("Halstead Metrics Analysis Report for " + file.getName());
				Font font1 = new Font(Font.FontFamily.HELVETICA, 25, Font.BOLD);
				Paragraph paragraph = new Paragraph("Halstead Metrics Analysis Report for " + file.getName()+"\n", font1);
				paragraph.setAlignment(Element.ALIGN_CENTER);
				border.setActive(true);
				document.add(paragraph);
				border.setActive(false);
				Font font2 = new Font(Font.FontFamily.HELVETICA, 12, Font.BOLD);
				paragraph = new Paragraph("File Name : " + file.getName(), font2);
				document.add(paragraph);
				Font font3 = new Font(Font.FontFamily.HELVETICA, 12, Font.BOLD | Font.UNDERLINE);
				paragraph = new Paragraph("Operators:", font3);
				document.add(paragraph);
				PdfPTable table = new PdfPTable(2);
				table.setSpacingBefore(10f);
				table.setSpacingAfter(10f);
				PdfPCell cell1 = new PdfPCell(new Paragraph("Name", font2));
				cell1.setPadding(5);
				cell1.setBackgroundColor(BaseColor.GRAY);
				cell1.setBorder(Rectangle.BOX);
				cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
				cell1.setBorderColor(BaseColor.GRAY);
				table.addCell(cell1);
				cell1 = new PdfPCell(new Paragraph("Count", font2));
				cell1.setPadding(5);
				cell1.setBackgroundColor(BaseColor.GRAY);
				cell1.setBorder(Rectangle.BOX);
				cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
				cell1.setBorderColor(BaseColor.GRAY);
				table.addCell(cell1);
				Font tFont = new Font(Font.FontFamily.HELVETICA, 12);
				for (int i = 0; i < Operators.getInstance().name.size(); ++i) {
					cell1 = new PdfPCell(new Paragraph(Operators.getInstance().name.get(i).toString(), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(Operators.getInstance().count.get(i).toString(), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
				}
				document.add(table);
				
				
				paragraph = new Paragraph("Operands:", font3);
				document.add(paragraph);
				table = new PdfPTable(2);
				table.setSpacingBefore(10f);
				table.setSpacingAfter(10f);
				cell1 = new PdfPCell(new Paragraph("Name", font2));
				cell1.setPadding(5);
				cell1.setBackgroundColor(BaseColor.GRAY);
				cell1.setBorder(Rectangle.BOX);
				cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
				cell1.setBorderColor(BaseColor.GRAY);
				table.addCell(cell1);
				cell1 = new PdfPCell(new Paragraph("Count", font2));
				cell1.setPadding(5);
				cell1.setBackgroundColor(BaseColor.GRAY);
				cell1.setBorder(Rectangle.BOX);
				cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
				cell1.setBorderColor(BaseColor.GRAY);
				table.addCell(cell1);
				tFont = new Font(Font.FontFamily.HELVETICA, 12);
				for (int i = 0; i < Operands.getInstance().name.size(); ++i) {
					cell1 = new PdfPCell(new Paragraph(Operands.getInstance().name.get(i).toString(), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(Operands.getInstance().count.get(i).toString(), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
				}
				document.add(table);
				
				
				paragraph = new Paragraph("Values", font3);
				document.add(paragraph);
				table = new PdfPTable(2);
				table.setSpacingBefore(10f);
				table.setSpacingAfter(10f);
				tFont = new Font(Font.FontFamily.HELVETICA, 12);
					cell1 = new PdfPCell(new Paragraph("No of Distinct Operators(n1)", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.n1), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					
					cell1 = new PdfPCell(new Paragraph("No of Distinct Operands(n2)", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.n2), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					
					cell1 = new PdfPCell(new Paragraph("Total No of Operators(N1)", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.N1), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);

					cell1 = new PdfPCell(new Paragraph("Total No of Operands(N2)", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.N2), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Program Length", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.PROGRAM_LENGTH), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Program Vocabulary", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.PROGRAM_VOCABULARY), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Estimated Length", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.ESTIMATED_LENGTH), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Purity Ratio", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.PURITY_RATIO), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Volume", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.VOLUME), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Difficulty", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.DIFFICULTY), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Program Effort", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.PROGRAM_EFFORT), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
					

					cell1 = new PdfPCell(new Paragraph("Programming Time", tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setBackgroundColor(BaseColor.GRAY);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.BLACK);
					table.addCell(cell1);
					cell1 = new PdfPCell(new Paragraph(String.valueOf(me.PROGRAMMING_TIME), tFont));
					cell1.setPadding(5);
					cell1.setBorder(Rectangle.BOX);
					cell1.setHorizontalAlignment(Element.ALIGN_CENTER);
					cell1.setBorderColor(BaseColor.GRAY);
					table.addCell(cell1);
				document.add(table);
				
				paragraph = new Paragraph("Copyright \u00a9  Specksboy Inc. 2014-15\n", font1);
				paragraph.setAlignment(Element.ALIGN_CENTER);
				border.setActive(true);
				document.add(paragraph);
				border.setActive(false);
				document.close();
			} catch (DocumentException e) {
				e.printStackTrace();
			}
			Desktop.getDesktop().open(outputFile);
			return true;
		} else {
			return false;
		}
	}
}
