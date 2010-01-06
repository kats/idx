using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.UI;

namespace Kontur.WebPFR
{
	public partial class reportview : UserControl
	{
		protected void Page_Load(object sender, EventArgs e)
		{
			if(DC == null || DC.Report == null) Visible = false;
		}

		protected string GetFilesHtml()
		{
			var html = new StringBuilder();
			foreach(var doc in DC.Report.Documents.Where(d => d.Type != DocumentType.reportDescription)) // TODO: OrderBy(...)
			{
				html.AppendFormat("<li><strong>{0}</strong><span>{1}</span>", 
					TypeToString(doc.Type), doc.FileName);
			}
			return html.ToString();
		}

		protected string GetSignature()
		{
			var sign = DC.Report.Signatures.Where(
				s => s.SignatureType != SignatureType.pfrRepresentative).FirstOrDefault();
			byte[] content = GetContent(sign.KansoOffset, sign.ContentLen);
			return new SignatureHtmlHelper().GetSignatureDescr_Org(content);
		}

		byte[] GetContent(long off, int len)
		{
			byte[] buf = new byte[len];
			using(var r = new FileStream("content", FileMode.Open))
			{
				r.Seek(off, SeekOrigin.Begin);
				r.Read(buf, 0, len);
				return buf;
			}
		}

		string TypeToString(DocumentType t)
		{
			switch(t)
			{
				case DocumentType.bunch: return "Индивидуальные сведения СЗВ-4";
				case DocumentType.advBunch: return "Ведомость уплаты страховых взносов АДВ-11";
				case DocumentType.reportAttachment: return "Неформализованное приложение";
				default: return "Неопознанный тип";
			}
		}

		public DCInfo DC {get; set;}
	}
}
