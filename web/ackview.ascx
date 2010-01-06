<%@ Control Language="C#" AutoEventWireup="true" Inherits="Kontur.WebPFR.ackview" %>
<div id="ackView" class="view">
	<script type="text/javascript">
		ackController = {
			load: function() {
				var reDate = /<датаВремяПолучения>([^<]+)<\/датаВремяПолучения>/;
				var reCode = /<регистрационныйНомерОрганизации>([^<]+)<\/регистрационныйНомерОрганизации>/;
				var reBunch = /<пачка>\s*<идентификаторДокумента>([^<]+)<\/идентификаторДокумента>\s*<имяФайла>([^<]+)<\/имяФайла>\s*<\/пачка>/g;
				var reAtt = /<приложение>\s*<идентификаторДокумента>([^<]+)<\/идентификаторДокумента>\s*<имяФайла>([^<]+)<\/имяФайла>\s*<\/приложение>/g;
				var xml = slApp.content.unzipper.UnzipAndDecodeXml(crypt.decrypt("<-%=content%>"));
				var date = convertXsdDateTime(xml.match(reDate)[1]);
				var code = xml.match(reCode)[1];
				$("#ackView")
					.prepend("<div>Регистрационный номер организации: <strong>" + code + "</strong>.</div>")
					.prepend("<div>Подтверждение сформировано <strong>" + date.date + "</strong>, в <strong>" + date.time + "</strong>.</div>");
				var file;
				while ((file = reBunch.exec(xml)) != null)
					$("#ackView ul").append("<li>" + file[2]);
				while ((file = reAtt.exec(xml)) != null)
					$("#ackView ul").append("<li>" + file[2]);
			}
		}
	</script>
	<h2>Подтверждение о получении</h2>
	<span class="signature">Подписано: <a href="#"><%=GetSignature()%></a></span>
</div>
