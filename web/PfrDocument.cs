using System;

namespace Kontur.WebPFR
{
	public class PfrDocument
	{
		public PfrDocument(Guid id, DocumentType type, int formKey, string fileName, long kansoOffset, int contentLen)
		{
			this.id = id;
			this.type = type;
			this.formKey = formKey;
			this.fileName = fileName;
			this.contentLen = contentLen;
			this.kansoOffset = kansoOffset;
		}

		public override string ToString()
		{
			return string.Format("id={0}, type={1}, formKey={2}, fileName={3}, len={4}, off={5}", id, type.ToString(), formKey, fileName, contentLen, kansoOffset);
		}

		public bool Equals(PfrDocument other)
		{
			if(ReferenceEquals(null, other)) return false;
			if(ReferenceEquals(this, other)) return true;
			return other.id.Equals(id) && Equals(other.type, type)  && Equals(other.formKey, formKey) && Equals(other.fileName, fileName) && other.contentLen == contentLen && other.kansoOffset == kansoOffset;
		}

		public override bool Equals(object obj)
		{
			if(ReferenceEquals(null, obj)) return false;
			if(ReferenceEquals(this, obj)) return true;
			if(obj.GetType() != typeof(PfrDocument)) return false;
			return Equals((PfrDocument)obj);
		}

		public override int GetHashCode()
		{
			unchecked
			{
				int result = id.GetHashCode();
				result = (result * 397) ^ type.GetHashCode();
				result = (result * 397) ^ formKey;
				result = (result * 397) ^ fileName.GetHashCode();
				result = (result * 397) ^ contentLen;
				result = (result * 397) ^ kansoOffset.GetHashCode();
				return result;
			}
		}

		public static bool operator ==(PfrDocument left, PfrDocument right) { return Equals(left, right); }
		public static bool operator !=(PfrDocument left, PfrDocument right) { return !Equals(left, right); }

		public Guid Id { get { return id; } }
		public DocumentType Type { get { return type; } }
		public int FormKey { get { return formKey; } }
		public string FileName { get { return fileName; } }
		public int ContentLen { get { return contentLen; } }
		public long KansoOffset { get { return kansoOffset; } }

		private readonly Guid id;
		private readonly DocumentType type;
		private readonly int formKey;
		private readonly string fileName;
		private readonly int contentLen;
		private readonly long kansoOffset;
	}
}
