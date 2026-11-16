# Week 4 Writeup — Agent-Ready Link Shortener

**Agent used:** Claude Code
**Task implemented:** #1 Custom alias

## 1. What I put in AGENTS.md and why it is broadly available

AGENTS.md içerisine servisin işlevi, dosya yapısı tablosu, temel komutlar (pytest, uvicorn), kapsam sınırları (product boundaries), SQL ve route yazım kuralları (conventions) ile 4 adımlı değişiklik iş akışını ekledim. Bu bilgiler, agent hangi görevi alırsa alsın kodun mimarisini bozmaması ve doğrulamayı hatasız yapması için evrenseldir. Örneğin "Out of scope" sınırları bulunmasaydı agent, basit bir alias özelliği eklerken projeye gereksiz yere SQLAlchemy ORM kurabilir, auth katmanı ekleyebilir veya main.py tek dosya düzenini parçalayabilirdi.

## 2. The scoped instruction and when it loads

Kapsamlanan talimat tests/ dizini altındaki test yazım kurallarıdır (tests/AGENTS.md ve bunu referans alan tests/CLAUDE.md). Bu talimat yalnızca agent tests/ dizini altındaki bir dosyayı açıp okuduğunda tetiklenir. Agent'ın context penceresi sınırlı bir kaynaktır; sadece main.py dosyasındaki küçük bir hatayı düzeltirken test fixture detaylarını veya assertion kurallarını bağlama yüklemek token israfına yol açar ve modelin odağını dağıtır. Claude Code bu talimatı, tests/ klasörüne odaklandığı anda dizine özel CLAUDE.md üzerinden dinamik olarak bağlama dahil ederek bulur.

## 3. The procedure my reusable workflow encodes

.claude/skills/implement-task/SKILL.md içindeki iş akışı; görevi ve mevcut kodu anlama, beklenen davranışı tanımlama, önce fail eden testi yazma, bunu geçirecek en küçük değişikliği yapma, pytest ile doğrulama ve riskleri özetleme adımlarını standart bir TDD sürecine dönüştürür. Testin önce fail etmesi (red-green döngüsü), testin yeni davranışı gerçekten ölçtüğünü ve tesadüfi bir pozitif sonuç vermediğini doğrulamak için kritik bir kontroldür. Bu süreci bir skill haline getirmek; kritik adımların atlanma riskini ciddi ölçüde azaltır, her seferinde uzun prompt yazma ihtiyacını ortadan kaldırır ve agent'ın çok daha tutarlı bir akışla çalışmasını sağlar.

## 4. How Claude Code discovers or invokes each artifact

Claude Code, kök dizindeki CLAUDE.md dosyasını oturum başlar başlamaz otomatik olarak okur; bu dosyanın içindeki @AGENTS.md direktifi sayesinde genel rehber ana bağlama aktarılır. tests/CLAUDE.md ise yalnızca agent tests/ altındaki bir dosyaya eriştiğinde devreye girer. Reusable workflow olan skill, kullanıcı tarafından /implement-task 1 komutuyla doğrudan çağrılır ya da model SKILL.md içindeki açıklama alanı ile görevin eşleştiğini fark ettiğinde bunu otonom olarak seçer. AGENTS.md genel bir standart olarak Cursor ve Codex gibi diğer yapay zeka araçları tarafından doğrudan okunurken, CLAUDE.md Claude Code ekosisteminin yerel giriş kapısı olduğu için iki yapı birbirini tamamlayacak şekilde konumlandırılmıştır.

## 5. What planning and review identified

Planlama aşamasında model, serbest bir alias ("c" gibi) verildiğinde gelecekteki otomatik base62 üretiminin aynı kodla çakışıp veritabanında 500 hatası doğuracağını erkenden fark etti; bu açığı free_code() yardımcı fonksiyonunu tasarlayarak giderdi. Ayrıca /docs ve /openapi.json gibi sistem yollarının alias olarak ezilmesini önlemek için rezerve liste mekanizması planlandı. Review aşamasında ilk sonuç doğrudan onaylanmayıp REVISE olarak işaretlendi; çünkü alias uzunluk sınırlarının testlerde tam kapsanmadığı ve README'nin güncellenmediği yakalandı. Bu eksikler giderildikten sonra kod ACCEPT aldı.

## 6. What I learned about structuring a repository for coding agents

Agent-native bir depo kurgularken en çarpıcı deneyim, bağlam yönetiminde "az ama doğru bilginin" her şeyi tek bir dosyaya yığmaktan çok daha verimli çalıştığını görmek oldu. Modelin tüm kuralları tek seferde ezberlemesi yerine; temel mimari sınırları kök rehbere bırakıp, test gibi özel yönergeleri klasör bazlı tetikleyicilerle izole etmenin bağlam kirliliğini ve aşırı mühendislik (over-engineering) eğilimini belirgin şekilde azalttığını gözlemledim. Bu modüler context yapısını, TDD odaklı skill disiplinini ve harici bir review aşamasıyla yapılan kontrolleri gelecekteki projelerimde güvenli kod geliştirmek için kesinlikle uygulayacağım.
