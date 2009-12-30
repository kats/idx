namespace Kontur.WebPFR
{
	public enum TransactionType :byte 
	{
		report,
		reportAcknowledgement,
		protocol,
		protocolReceipt,
		registration,
		reportSendError,
		protocolReceiptSendError,
		registrationSendError
	}

	public enum CorrectionType 
	{
		Indefinite,
		Corrective,
		Abrogative
	}

	public enum DocumentType :byte
	{
		bunch,
		advBunch,
		dsvBunch,
		dsvRegistry,
		zpfBunch,
		zvukBunch,
		reportDescription,
		reportAttachment,
		reportAcknowledgement,
		protocol,
		protocolAppendix,
		info,
		registrationRequest,
		error
	}

	public enum SignatureType :byte
	{
		chief, 
		pfrBookkeeper,
		pfrRepresentative 
	}
}
