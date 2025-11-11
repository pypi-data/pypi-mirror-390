from catmail import Mailer, Reader, Scanner
from catmail import config as catfyg
from .config import config

mfg = config.mail
catfyg.set({
	"html": mfg.html,
	"gmailer": mfg.gmailer,
	"scantick": mfg.scantick,
	"verbose": mfg.verbose,
	"cache": config.cache
})
catfyg.admin.update("contacts", config.admin.contacts)
catfyg.admin.update("reportees", config.admin.reportees)

mailer = Mailer(mfg.mailer, mfg.name)
send_mail = mailer.mail
email_admins = mailer.admins
email_reportees = mailer.reportees

reader = Reader(config.mailer)
check_inbox = reader.inbox

scanner = Scanner(reader)
on_mail = scanner.on