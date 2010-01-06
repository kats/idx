using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.UI;

namespace Kontur.WebPFR
{
	public partial class protocolview : UserControl
	{
		protected void Page_Load(object sender, EventArgs e)
		{
			if(DC == null || DC.Protocol == null) Visible = false;
		}

		protected string GetFilesHtml()
		{
			int docNum = 0;
			var html = new StringBuilder();
			foreach(var doc in DC.Protocol.Documents
				.Where(d => d.Type == DocumentType.protocolAppendix))	
			{
				html.AppendFormat("<li><a href='#'>Приложение {0}</a>", docNum);
				++docNum;
			}
			return html.ToString();
		}

		protected string GetSignature()
		{
			var sign = DC.Protocol.Signatures.Where(
				s => s.SignatureType == SignatureType.pfrRepresentative).FirstOrDefault();
			byte[] content = GetContent(sign.KansoOffset, sign.ContentLen);
			return new SignatureHtmlHelper().GetSignatureDescr_Pfr(content);
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

		public DCInfo DC {get; set;}
	}
}
