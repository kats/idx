<%@ Control Language="C#" AutoEventWireup="true" Inherits="Kontur.WebPFR.protocolview" %>
<div id="protocolView" class="view">
	<script type="text/javascript">
		protocolController = {
			load: function() {
				xml = slApp.content.unzipper.UnzipAndDecodeXml(crypt.decrypt("<-%=content%>"));
				hasReceipt = "<-%=hasReceipt%>" == "True";
				this.writeProtocolInfo();
				this.fillAppendicesList();
				$("#protocolView #saveFiles").click(protocolController.saveFiles);
				
				if(hasReceipt) {
					$("#protocolView #signProtocol").hide();
					$("#protocolView #saveFiles").text("Сохранить все ЭЦП...");
					}
				else $("#protocolView #signProtocol").click(protocolController.signProtocol);
			},
			loadDocAsync: function(id, callback) {
				$.ajax({
					async: true,
					dataType: "text",
					processData: false,
					type: "GET",
					url: "document.ashx?packageId=<-%=packageId%>&docId=" + id,
					cache: false,
					success: function(data) { if (callback !== undefined) callback(data); },
					error: function() { alert('ajax error'); }
				});
			},
			loadDocSync: function(id) {
				return $.ajax({
					async: false,
					dataType: "text",
					processData: false,
					type: "GET",
					url: "document.ashx?packageId=<-%=packageId%>&docId=" + id,
					cache: false,
					error: function(e) { alert(e); }
				}).responseText;
			},
			loadSignSync: function(id) {
				return $.ajax({
					async: false,
					dataType: "text",
					processData: false,
					type: "GET",
					url: "signature.ashx?mode=b64&type=pfrRepresentative&packageId=<-%=packageId%>&docId=" + id,
					error: function(e) { alert(e); }
				}).responseText;
			},
			loadSignSync2: function(id) {
				return $.ajax({
					async: false,
					dataType: "text",
					processData: false,
					type: "GET",
					url: "signature.ashx?mode=b64&type=pfrBookkeeper&packageId=<-%=receiptId%>&docId=" + id,
					error: function(e) { alert(e); }
				}).responseText;
			},
			loadProtocolText: function(id) {
				this.loadDocAsync(id, this.setProtocolText);
			},
			signDoc: function(id) {
				//var signId = slApp.content.reportBuilder.CreateSignId();
				//var docContent = this.loadDocSync(id);
				//var signContent = crypt.sign(docContent, orgProps.chiefCertNum);
			    var signId = slApp.content.reportBuilder.CreateSignId();
                var encrypted = this.loadDocSync(id);
                var decrypted = crypt.decrypt(encrypted); 
                var docContent = slApp.content.unzipper.Unzip(decrypted);
                var signContent = crypt.sign(docContent, orgProps.chiefCertNum);

				$.ajax({
					async: false,
					data: signContent,
					dataType: "text",
					processData: false,
					type: "POST",
					url: "put_content.aspx?docId=" + signId,
					error: function() { alert('ajax error'); }
				});
				return signId;
			},
			signProtocol: function() {
				var apps = xml.substring(xml.search(/<\/подтверждениеПолучения>/));
				var reApp = /<приложение>\s*<идентификаторДокумента>([^<]+)<\/идентификаторДокумента>\s*<имяФайла>([^<]+)<\/имяФайла>\s*<\/приложение>/g;
				var file;
				var protocolReceipt = "";
				while ((file = reApp.exec(apps)) != null) {
					var id = file[1];
					var signId = protocolController.signDoc(id);
					protocolReceipt += id + ":" + signId + ";";
				}
				var id = "<-%=protocolId%>";
				var signId = protocolController.signDoc(id);
				protocolReceipt += id + ":" + signId + ";";

				// send protocol receipt
				$.ajax({
					async: false,
					dataType: "text",
					processData: false,
					type: "POST",
					url: "sign_protocol.aspx?dcId=<-%=dcId%>&protocolReceipt=" + protocolReceipt,
					error: function() { alert('ajax error'); },
					success: window.location.reload
				});

			},
			fillAppendicesList: function() {
				var showList = false;
				var atts = xml.substring(xml.search(/<\/подтверждениеПолучения>/));
				var reAtt = /<приложение>\s*<идентификаторДокумента>([^<]+)<\/идентификаторДокумента>\s*<имяФайла>([^<]+)<\/имяФайла>\s*<\/приложение>/g;
				var file;
				while ((file = reAtt.exec(atts)) != null) {
					var id = file[1];
					var name = file[2];
					if (name == "protocol.txt")
						this.loadProtocolText(id);
					else {
						showList = true;
						var li = $("#protocolView #appendices #l2")
							.append("<li>" + name + "<ul>" + signatures[id] + "</ul></li>")
					}
				}
				if (showList) $("#protocolView #appendices").show();
				
			},
			writeProtocolInfo: function() {
				var date = convertXsdDateTime(xml.match(/<датаВремяОтправки>([^<]+)<\/датаВремяОтправки>/)[1]);
				var positive = convertXsdBoolean(xml.match(/<являетсяПоложительным>([^<]+)<\/являетсяПоложительным>/)[1]);
				var code = xml.match(/<регистрационныйНомерОрганизации>([^<]+)<\/регистрационныйНомерОрганизации>/)[1];
				$("a[href='#protocol']").addClass(positive ? "positive" : "negative");
				$("#protocolView #protocolText").addClass(positive ? "positive" : "negative");
				var msg = positive ? "сведения приняты успешно" : "при проверке сведений были обнаружены ошибки";
				$("#protocolView #info")
					.prepend("<div>Результат проверки: <strong>" + msg + "</strong>.</div>")
					.prepend("<div>Регистрационный номер организации: <strong>" + code + "</strong>.</div>")
					.prepend("<div>Протокол сформирован <strong>" + date.date + "</strong>, в <strong>" + date.time + "</strong>.</div>");
			},
			setProtocolText: function(data) {
				if(data == undefined || data == "") return;
				$("#protocolView #comment #protocolText").text(slApp.content.unzipper.UnzipAndDecodeXml(crypt.decrypt(data)));
				$("#protocolView #comment").show();
			},
			saveFiles: function() {
				var comDialogs = new ActiveXObject("Kontur.ComDlgs");
				var bin = new ActiveXObject("SKBKontur_LIT_CryptoCOM.BinaryObjectService");

				var folder = comDialogs.SelectFolderDialog();
				if (folder === null || folder == "") return;

				var apps = xml.substring(xml.search(/<\/подтверждениеПолучения>/));
				var reApp = /<приложение>\s*<идентификаторДокумента>([^<]+)<\/идентификаторДокумента>\s*<имяФайла>([^<]+)<\/имяФайла>\s*<\/приложение>/g;
				var file;
				while ((file = reApp.exec(apps)) != null) {
					var id = file[1];
					if(!hasReceipt) {
						var unzipped = slApp.content.unzipper.Unzip(crypt.decrypt(protocolController.loadDocSync(id)));
						var bo = bin.BinaryObjectFromBase64(unzipped);
						bin.BinaryObjectToFile(bo, folder + "\\" + file[2]);
					} else {
						var bo = bin.BinaryObjectFromBase64(protocolController.loadSignSync2(id));
						bin.BinaryObjectToFile(bo, folder + "\\" + file[2] + ".org.sign");
					}
					var bo = bin.BinaryObjectFromBase64(protocolController.loadSignSync(id));
					bin.BinaryObjectToFile(bo, folder + "\\" + file[2] + ".pfr.sign");
				}
				var unzipped = slApp.content.unzipper.Unzip(crypt.decrypt(protocolController.loadDocSync("<-%=protocolId%>")));
				var bo = bin.BinaryObjectFromBase64(unzipped);
				bin.BinaryObjectToFile(bo, folder + "\\protocol.xml");
				bo = bin.BinaryObjectFromBase64(protocolController.loadSignSync("<-%=protocolId%>"));
				bin.BinaryObjectToFile(bo, folder + "\\protocol.xml.pfr.sign");
				if(hasReceipt) {
    				bo = bin.BinaryObjectFromBase64(protocolController.loadSignSync2("<-%=protocolId%>"));
    				bin.BinaryObjectToFile(bo, folder + "\\protocol.xml.org.sign");
				}
			}
		}
		signatures = {<-%=GetSignaturesJson() %>}
	</script>
	<h2>Протокол приема и приложения</h2>
	<ol id="files">
		<%=GetFilesHtml() %>
	</ol>
	<span class="signature">Подписано: <a href="#"><%=GetSignature()%></a></span>
</div>
