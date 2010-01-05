using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System;

namespace Kontur.WebPFR
{
	public partial class list : System.Web.UI.Page
	{
		protected string Url = "list.aspx?";
		protected int PageCount = 1;
		protected int page;
		protected const int page_size = 20;
		
		List<DCInfo> dcs;

		protected void Page_Load(object sender, EventArgs e)
		{
			if(!int.TryParse(Request["page"], out page)) page = 0;
			dcs = GetDCs();
			dcs.Sort((a,b) => b.Time.CompareTo(a.Time));
			PageCount = dcs.Count() / page_size;
		}

		private List<DCInfo> GetDCs()
		{
			var grps = from txn in new IndexReader().GetTransactions() 
				group txn by txn.DcId into grp 
				select grp;
			var dcs = new List<DCInfo>();
			foreach(var grp in grps) dcs.Add(new DCInfo(grp));
			return dcs;
		}

		protected string Word()
		{
			int c = PageCount;
			int l2 = c - c/100*100;
			if(l2 >= 5 && l2 <= 20) return "страниц";
			int l1 = l2 - l2/10*10;	
			if(l1 == 1) return "страница";
			if(l1 >= 2 && l1 <= 4) return "страницы";
			return "страниц";
		}

		protected string PrevHref()
		{
			if(page > 0)
				return string.Format("<span>&larr;</span><a href='{0}'>Предыдущая</a>", PageHref(page-1));
			return string.Format("<span class='no'>&larr;</span><a class='no'>Предыдущая</a>");
		}

		protected string NextHref()
		{
			if(page < PageCount-1)
				return string.Format("<a href='{0}'>Следующая</a><span>&rarr;</span>", PageHref(page+1));
			return string.Format("<a class='no'>Следующая</a><span class='no'>&rarr;</span>");
		}

		protected string PageHref(int p)
		{
			return string.Format("{0}page={1}", Url, p);
		}

		protected string GetRows()
		{
			var buf = new StringBuilder();
			for(int i = Math.Max(page*page_size, 0); 
					i < Math.Min((page+1)*page_size, dcs.Count()); ++i)
			{
				var dc = dcs[i];
				buf.AppendFormat(
					"<tr><td class='status'>{0}</td><td>{1}</td><td>{2}</td><td>{3:dd.MM.yyyy}</td></tr>",
					 StatusToText(dc), 
					 LinkText(dc), 
					 dc.Upfr, 
					 dc.Time);
			}
			return buf.ToString();
		}

		string StatusToText(DCInfo dc) 
		{
			switch(dc.Progress)
			{
				case TransactionType.report: return "Отправлены";
				case TransactionType.reportAcknowledgement: return "Получены";
				case TransactionType.protocol:
					return dc.Positive ? 
						"<span class='acc'>Приняты</span>, <span class='sign'>подпишите протокол</span>" :
						"<span class='rej'>Не приняты</span>, <span class='sign'>подпишите протокол</span>";
				case TransactionType.protocolReceipt:
					return dc.Positive ?
						"<span class='acc'>Приняты</span>" :
						"<span class='rej'>Не приняты</span>";
				default: return "<span class='err'>Ошибка отправки</span>";
			}
		}

		string LinkText(DCInfo dc)
		{
			return string.Format("<a href='dc.aspx?dcId={0}'>{1}</a> ({2})",
				dc.DcId, 
				fn.TypeToString(dc.Type),
				fn.CorrYearString(dc.Type, dc.Corr, dc.Year));
		}
	}
}
