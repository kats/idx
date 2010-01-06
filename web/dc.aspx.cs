using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

namespace Kontur.WebPFR
{
	public partial class dcpage : System.Web.UI.Page
	{
		protected Guid dcId;
		protected DCInfo dc;
		protected reportview reportView;
		protected ackview ackView;
		protected protocolview protocolView;
			
		protected void Page_Load(object sender, EventArgs e)
		{
			dcId = new Guid(Request["dcId"]);
			dc = GetDC(dcId);

			reportView.DC = dc;
			ackView.DC = dc;
			protocolView.DC = dc;
		}

		protected string DescrStr()
		{
			return string.Format("{0} ({1}, в УПФР: {2}, отправлены: {3:dd.MM.yyyy} в {4:hh:mm})",
				fn.TypeToString(dc.Type),
				fn.CorrYearString(dc.Type, dc.Corr, dc.Year),
				dc.Upfr, dc.Time, dc.Time);
		}

		// TODO (kats): controls instead of html generation.
		protected string StatusText()
		{
			switch(dc.Progress)
			{
				case TransactionType.report: 
					return "<span>Сведения отправлены в УПФР.</span><strong>Ожидайте подтверждение о получении.</strong>";
				case TransactionType.reportAcknowledgement: 
					return "<span>Сведения получены УПФР.</span><strong>Ожидайте ответ из УПФР.</strong>";
				case TransactionType.protocol: 
					return string.Format("<span>Сведения проверены УПФР: получен протокол приема.</span><strong>Сведения {0}. Подпишите протокол приема и приложения.</strong>",
							dc.Positive ? "приняты" : "не приняты");
				case TransactionType.protocolReceipt: 
					return string.Format("<span>Сведения проверены УПФР: получен протокол приема.</span><strong>Сведения {0}. Передача сведений завершена.</strong>",
							dc.Positive ? "приняты" : "не приняты");
				default: return "<span></span><strong></strong>";
			}
		}

		protected string StatusClass()
		{
			switch(dc.Progress)
			{
				case TransactionType.report: return "neutral";
				case TransactionType.reportAcknowledgement: return "neutral";
				case TransactionType.protocol: 
				case TransactionType.protocolReceipt: return dc.Positive ? "positive" : "negative";
				default: return "negative";
			}
		}

		DCInfo GetDC(Guid dcId)
		{
			return new DCInfo(from txn in new IndexReader().GetTransactions() where txn.DcId == dcId select txn);
		}
	}
}
