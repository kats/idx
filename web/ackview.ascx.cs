using System;
using System.IO;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;

namespace Kontur.WebPFR
{
	public partial class ackview : UserControl
	{
		protected void Page_Load(object sender, EventArgs e)
		{
			if(DC == null || DC.ReportAcknowledgement == null) Visible = false;
		}


		protected string GetSignature()
		{
			var sign = DC.ReportAcknowledgement.Signatures.FirstOrDefault();
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
