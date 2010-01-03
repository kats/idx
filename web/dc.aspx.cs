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


		protected void Page_Load(object sender, EventArgs e)
		{
			dcId = new Guid(Request["dcId"]);
			dc = GetDC(dcId);
		}

		protected string DescrStr()
		{
			return string.Format("{0} ({1}, в УПФР: {2}, отправлены: {3:dd.MM.yyyy} в {4:hh:mm})",
				fn.TypeToString(dc.Type),
				fn.CorrYearString(dc.Type, dc.Corr, dc.Year),
				dc.Upfr, dc.Time, dc.Time);
		}

		// TODO: всё не так
		protected bool Positive { get {return 
			dc.Status == DCStatus.Acc_Fin || dc.Status == DCStatus.Acc_Sign;}}

		DCInfo GetDC(Guid dcId)
		{
			return GetDCInfo(
				from txn in GetTransactions() where txn.DcId == dcId select txn);
		}
		
		IEnumerable<PfrTransaction> GetTransactions()
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
	}
}
