using System;
using System.IO;
using System.Collections.Generic;

namespace Kontur.WebPFR
{
	public class IndexReader
	{
		public IEnumerable<PfrTransaction> GetTransactions()
		{
			using(var file = new StreamReader("resp111"))
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
