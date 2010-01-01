using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System;

namespace Kontur.WebPFR
{
	enum DCStatus {Sent, Acc_Sign, Rej_Sign, Acc_Fin, Rej_Fin, Received, Error}
	enum DCType {adv, dsv, dsvReg, zpf, zvuk}
	class DCInfo
	{
		public DCInfo(DCStatus status, string upfr, DCType type, Guid dcId, DateTime time, CorrectionType corr, int year) 
		{
			Status=status; Upfr=upfr; Type=type; DcId=dcId; Time=time; Corr=corr; Year=year;
		}

		public string Upfr;
		public Guid DcId;
		public DateTime Time;
		public CorrectionType Corr;
		public int Year;
		public DCStatus Status;
		public DCType Type;
	}

	public partial class list : System.Web.UI.Page
	{
		protected string Url = "list.aspx?";
		protected int Count = 10;
		protected int page;
		protected const int page_size = 20;

		protected void Page_Load(object sender, EventArgs e)
		{
			if(!int.TryParse(Request["page"], out page)) page = 0;
		}

		protected string Word()
		{
			int c = Count;
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
				return string.Format("<span>&larr;</span><a href='{0}'>Предыдущая</a>", Page(page-1));
			return string.Format("<span class='no'>&larr;</span><a class='no'>Предыдущая</a>");
		}

		protected string NextHref()
		{
			if(page < Count-1)
				return string.Format("<a href='{0}'>Следующая</a><span>&rarr;</span>", Page(page+1));
			return string.Format("<a class='no'>Следующая</a><span class='no'>&rarr;</span>");
		}

		protected string Page(int p)
		{
			return string.Format("{0}page={1}", Url, p);
		}

		protected string GetRows()
		{
			var buf = new StringBuilder();
			var dcs = from txn in Rows() 
				group txn by txn.DcId into grp 
				select grp;
			// TODO: нормальный пейджинг
			int i = 0;
			foreach(var t in dcs)
			{
				DCInfo dc = GetDCInfo(t);
				buf.AppendFormat(
					"<tr><td class='status'>{0}</td><td>{1}</td><td>{2}</td><td>{3:dd.MM.yyyy}</td></tr>",
					 StatusToText(dc.Status), 
					 LinkText(dc), 
					 dc.Upfr, 
					 dc.Time);
			}
			return buf.ToString();
		}

		string StatusToText(DCStatus s) 
		{
			switch(s)
			{
				case DCStatus.Sent: return "Отправлены";
				case DCStatus.Received: return "Получены";
				case DCStatus.Acc_Sign: return "<span class='acc'>Приняты</span>, <span class='sign'>подпишите протокол</span>";
				case DCStatus.Rej_Sign: return "<span class='rej'>Не приняты</span>, <span class='sign'>подпишите протокол</span>";
				case DCStatus.Acc_Fin: return "<span class='acc'>Приняты</span>";
				case DCStatus.Rej_Fin: return "<span class='rej'>Не приняты</span>";
				case DCStatus.Error: return "<span class='err'>Ошибка отправки</span>";
				default: return "";
			}
		}

		string LinkText(DCInfo dc)
		{
			return string.Format("<a href='dc.aspx?dcId={0}'>{1}</a>{2}",
				dc.DcId, 
				TypeToString(dc.Type),
				dc.Type == DCType.adv ? CorrYearStr(dc.Corr, dc.Year) : "");
		}

		string CorrYearStr(CorrectionType c, int y)
		{
			return string.Format(" ({0}за {1} год)", 
				c == CorrectionType.Abrogative ? "отменяющие " : 
				c == CorrectionType.Corrective ? "корректирующие " : "", y);
		}

		string TypeToString(DCType t)
		{
			switch(t)
			{
				case DCType.adv: return "Годовая отчетность"; 
				case DCType.dsv: return "Заявление о вступлении в систему добровольного страхования";
				case DCType.dsvReg: return "Реестр лиц, за которых перечислены дополнительные страховые взносы";
				case DCType.zpf: return "Заявление о переходе в НПФ";
				case DCType.zvuk: return "Заявление о выборе управляющей компании";
				default: return "";
			}
		}

		DCInfo GetDCInfo(IEnumerable<PfrTransaction> txns)
		{
			var dcId = txns.First().DcId;
			var upfr = txns.First().UpfrCode;
			var corr = txns.First().CorrectionType;
			var year = txns.First().AccountingYear;
			var time = txns.Last().TransactionTime;
			var type = CalcType(txns);
			var status = CalcStatus(txns);
			return new DCInfo(status, upfr, type, dcId, time, corr, year);
		}

		DCStatus CalcStatus(IEnumerable<PfrTransaction> txns)
		{
			bool has_rep=false, has_ack=false, has_prot=false, has_rec=false;
			bool positive=false;
			int doc_hash=0, sign_hash=0;
			foreach(var txn in txns)
			{
				if(txn.Type == TransactionType.registrationSendError) return DCStatus.Error;
				if(txn.Type == TransactionType.protocolReceiptSendError) return DCStatus.Error;
				if(txn.Type == TransactionType.reportSendError) return DCStatus.Error;
				if(txn.Type == TransactionType.report) has_rep = true;
				if(txn.Type == TransactionType.reportAcknowledgement) has_ack = true;
				if(txn.Type == TransactionType.protocol) has_prot = true;
				if(txn.Type == TransactionType.protocolReceipt) has_rec = true;
				
				if(txn.Type == TransactionType.report) 
					doc_hash ^= Hash(txn.Documents);
				if(txn.Type == TransactionType.protocol) 
				{
					doc_hash ^= Hash(txn.Documents);
					sign_hash = Hash(txn.Signatures);
				}
			}
			positive = (doc_hash == sign_hash);

			if(has_rec) return positive ? DCStatus.Acc_Fin : DCStatus.Rej_Fin;
			if(has_prot) return positive ? DCStatus.Acc_Sign : DCStatus.Rej_Sign;
			if(has_ack) return DCStatus.Received;
			if(has_rep) return DCStatus.Sent;
			return DCStatus.Error;
		}

		DCType CalcType(IEnumerable<PfrTransaction> txns)
		{
			foreach(var txn in txns)
			{
				if(txn.Type == TransactionType.report)
				{
					foreach(var doc in txn.Documents)
					{
						switch(doc.Type)
						{
							case DocumentType.bunch: return DCType.adv;
							case DocumentType.advBunch: return DCType.adv;
							case DocumentType.dsvBunch: return DCType.dsv;
							case DocumentType.dsvRegistry: return DCType.dsvReg;
							case DocumentType.zpfBunch: return DCType.zpf;
							case DocumentType.zvukBunch: return DCType.zvuk;
						}
					}
				}
			}
			return DCType.adv;
		}

		int Hash(IEnumerable<PfrDocument> docs)
		{
			int hash = 0;
			foreach(var doc in docs) hash ^= doc.Id.GetHashCode();
			return hash;
		}

		int Hash(IEnumerable<PfrSignature> signs)
		{
			int hash = 0;
			foreach(var sign in signs) hash ^= sign.DocId.GetHashCode();
			return hash;
		}

		IEnumerable<PfrTransaction> Rows()
		{
			using(var file = new StreamReader("resp3"))
			{
				string[] head;
				while((head = ReadHead(file)) != null)
				{
					List<PfrDocument> docs = ReadDocs(file);
					List<PfrSignature> signs = ReadSigns(file);
					if(ReadTail(file)) 
					{
						yield return new PfrTransaction(
							new Guid(head[0]), new Guid(head[1]),
							new DateTime(Int64.Parse(head[2])),
							(TransactionType)Enum.Parse(typeof(TransactionType), head[3]),
							head[4].Trim(new char[]{'\"'}),
							Int32.Parse(head[5]),
							Int32.Parse(head[6]),
							(CorrectionType)Enum.Parse(typeof(CorrectionType), head[7]),
							docs, signs);
					}
				}
			}
		}

		string[] ReadHead(StreamReader file)
		{
			for(var row = file.ReadLine(); row != null; row = file.ReadLine())
			{
				var tuple = row.Split('\t');
				if(tuple.Length >= 8 && file.ReadLine() == "") return tuple;
			}
			return null;
		}

		List<PfrDocument> ReadDocs(StreamReader file)
		{
			var docs = new List<PfrDocument>();
			for(var row = file.ReadLine(); row != null; row = file.ReadLine())
			{
				if(row == "") return docs;
				var tuple = row.Split('\t');
				docs.Add(new PfrDocument(
					new Guid(tuple[0]), 
					(DocumentType)Enum.Parse(typeof(DocumentType), tuple[1]), 
					Int32.Parse(tuple[2]),
					tuple[3],
					Int64.Parse(tuple[4]),
					Int32.Parse(tuple[5])));
			}
			return null;
		}

		List<PfrSignature> ReadSigns(StreamReader file)
		{
			var signs = new List<PfrSignature>();
			for(var row = file.ReadLine(); row != null; row = file.ReadLine())
			{
				if(row == "") return signs;
				var tuple = row.Split('\t');
				signs.Add(new PfrSignature(
					new Guid(tuple[0]), 
					new Guid(tuple[1]), 
					(SignatureType)Enum.Parse(typeof(SignatureType), tuple[2]), 
					Int64.Parse(tuple[3]),
					Int32.Parse(tuple[4])));
			}
			return null;
		}

		bool ReadTail(StreamReader file)
		{
			return file.ReadLine() == "";
		}
	}
}
