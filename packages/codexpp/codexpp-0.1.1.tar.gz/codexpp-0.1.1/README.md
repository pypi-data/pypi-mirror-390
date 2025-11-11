 # Codexpp

Codexpp, OpenAI Codex CLI'yi yapılandırılmış yazılım geliştirme iş akışlarına dönüştüren hafif bir çerçevedir. SuperClaude Framework ve SuperGemini Framework'lerinden ilham alır; slash komutları, persona tabanlı çalışma modları ve proje odaklı davranış kuralları sağlar.
 
 ## Özellikler
 
 - **Slash Komutları:** TOML tabanlı komut tanımları sayesinde tekrar eden görevler için tutarlı istemler üretir.
 - **Persona Modu:** Analiz, uygulama veya kod inceleme gibi rollere uygun davranış yönergeleri içerir.
 - **Proje Entegrasyonu:** İstediğiniz kod deposunda `.codexpp` klasörünü kurup komut ve persona setlerini özelleştirebilirsiniz.
 - **Yerel Çalışma:** Tüm dosyalar yerel dizinlerde tutulur; Codex CLI'ye yönlendirmek istediğiniz çıktıyı siz kontrol edersiniz.
 - **CLI Aracı:** `codexpp` komutu ile komutları listeleyebilir, detaylarını inceleyebilir ve parametrik istemler üretebilirsiniz.
 - **Şablon Doğrulaması:** Slash komutlarındaki `{{placeholder}}` alanları otomatik kontrol edilir; tanımsız veya işlenmemiş ifadeler komut çalışmadan önce bildirilir.
- **Persona Senkronizasyonu:** `AGENTS.md` içeriğini ve Codex hafıza dosyanızı tek komutla güncel tutabilirsiniz.
 
 ## Kurulum

> Proje henüz PyPI üzerinde yayımlanmadığı için elle kurulum gerekir.

### UV ile (önerilen)

```bash
git clone https://github.com/avometre/codexpp.git
cd codexpp
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

Tek satırlık kurulum tercih ederseniz:

```bash
uv pip install git+https://github.com/avometre/codexpp.git
```

### pip ile

```bash
git clone https://github.com/avometre/codexpp.git
cd codexpp
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### PyPI (Yayınlandı!)

Paket PyPI'de yayında! Doğrudan kurulum yapabilirsiniz:

```bash
pip install codexpp
# veya
uv pip install codexpp
```

**PyPI Sayfası:** https://pypi.org/project/codexpp/

Kurulum sonrası `codexpp --help` ile CLI komutlarını doğrulayabilirsiniz. Codex CLI'nın (`npm i -g @openai/codex`) yüklü olması gerekir; `codexpp codex status` komutu ikiliyi bulamıyorsa Codex CLI'yi kurmayı unutmayın.

## Hızlı Başlangıç

İstediğiniz projede:
 
 ```bash
 codexpp bootstrap
 codexpp commands list
 codexpp commands render cx:analyze --set target=src/
 codexpp commands run cx:analyze --set target=src/ --persona system-architect --print-only
 codexpp commands run cx:analyze --set target=src/ --exec --codex-arg=--skip-git-repo-check
codexpp commands run cx:analyze --set target=src/ --summary-only
codexpp commands run cx:analyze --set target=src/ --summary --save-summary reports/summary.md
codexpp commands run cx:analyze --set target=src/ --print-only --save-prompt prompts/analyze.txt
codexpp commands list --verbose       # Parametreleri ve özetleri ayrıntılı göster
 ```
 
 `bootstrap`, mevcut dizine `.codexpp/commands` ve `.codexpp/personas` klasörlerini kopyalar. Dosyalardaki TOML tanımlarını düzenleyerek iş akışınızı özelleştirebilirsiniz.

`commands run`, slash komut istemini üretip isteğe bağlı olarak persona yönergeleriyle birleştirir. Varsayılan olarak istemi stdout'a yazar; `--exec` eklendiğinde istemi `codex exec` aracılığıyla Codex CLI'ye gönderir. Codex CLI'nin depo dışı çalışmasına izin vermek için `--codex-arg=--skip-git-repo-check` gibi ek argümanlar iletilebilir.
 
`{{` ifadesini metin olarak kullanmak istiyorsanız `\{{` yazarak kaçırabilirsiniz.

#### Placeholder İpuçları

- Placeholder anahtarları TOML dosyasında tanımlı olmalı; aksi halde komut çalışmadan önce hata alırsınız.
- Boşluklu tanımları destekler: `{{ target }}` ile `{{target}}` aynı şekilde işlenir.
- Kaçış yapmak için çift açılı parantezden önce ters bölü ekleyin: `\{{ literal }}` çıktıda `{{ literal }}` olarak görünür.
- `--summary` veya `--summary-only` bayrakları ile komut parametrelerinin ve persona seçimlerinin kısa planını görebilirsiniz.
- `--summary-format json|markdown|text` ile özet çıktısını istediğiniz formatta oluşturabilirsiniz (varsayılan `text`).

## Komut Referansı

### Varsayılan Komutlar

- `cx:analyze` (persona: `system-architect`) — Kod tabanının seçili bölümünü analiz eder, mimari özet, riskler ve takip adımlarını listeler. Parametreler: `target` (zorunlu), `context` (isteğe bağlı).
- `cx:implement` (persona önerisi: `implementation-engineer`) — Özellik veya görev uygulaması için plan çıkarır, kod değişikliklerini yönlendirir ve test önerir. Parametreler: `spec` (zorunlu), `notes` (isteğe bağlı).
- `cx:review` (persona: `code-reviewer`) — Diff ya da PR üzerinde kod incelemesi yapar; güçlü yönler, kritik sorunlar ve öneriler sunar. Parametreler: `diff_source` (zorunlu), `focus` (isteğe bağlı).
- `cx:triage` (persona önerisi: `system-architect`) — Hata raporlarını çözümlemek için olası kök nedenleri ve debug adımlarını üretir. Parametreler: `report` (zorunlu), `context` (isteğe bağlı).
- `cx:refactor` (persona önerisi: `implementation-engineer`) — Refaktör planı hazırlar, adımları ve test kapsamını belirler. Parametreler: `notes` (zorunlu), `goals` (isteğe bağlı).

### `extended` Komut Paketi

- `cx:plan` (persona: `implementation-engineer`) — Özellik gereksinimini görev parçalarına böler, bağımlılıkları ve riskleri çıkarır. Parametreler: `spec` (zorunlu), `hints` (isteğe bağlı).
- `cx:test` (persona: `code-reviewer`) — Değişiklik için gerekli test senaryolarını ve araç komutlarını listeler. Parametreler: `change` (zorunlu), `tests` (isteğe bağlı).
- `cx:doc` (persona: `implementation-engineer`) — Dokümantasyon güncellemelerini özetler, hedef kitlenin ihtiyaçlarını belirtir. Parametreler: `change` (zorunlu), `audience` (isteğe bağlı).

### `ops` Komut Paketi

- `cx:deploy` (persona: `implementation-engineer`) — Dağıtım planını, ön-koşulları, doğrulama ve rollback hazırlığını sunar. Parametreler: `notes` (zorunlu), `environment` (zorunlu).
- `cx:rollback` (persona: `implementation-engineer`) — Acil geri dönüş planı hazırlayıp iletişim ve takip adımlarını belirtir. Parametreler: `incident` (zorunlu), `version` (isteğe bağlı).
- `cx:status` (persona: `system-architect`) — Operasyonel durum raporu üretir, kritik metrikleri ve açık riskleri aktarır. Parametreler: `scope` (zorunlu), `metrics` (isteğe bağlı).

### Persona Kısayolları

- `system-architect` — Mimari vizyon, performans ve risk değerlendirmeleri.
- `implementation-engineer` — Uygulama adımları, kod detayları ve test kapsamı.
- `code-reviewer` — Değişiklik kalitesini değerlendirme, risk analizi ve geri bildirim.

Komutları çalıştırırken `--persona <kimlik>` bayrağı ile bu rolleri seçebilir veya `commands run` komutuna varsayılan personayı (`--persona system-architect` gibi) ekleyebilirsiniz.

### Komut Paketleri

Yapılandırılmış komut setini genişletmek için paketleri kullanabilirsiniz:

```bash
codexpp commands packs list
codexpp commands packs install extended --force    # extended.toml paketini projeye kurar
codexpp commands packs install extended --user     # Kullanıcı seviyesine kurar
codexpp commands packs install ops --force         # Operasyonel komutlar
```

`extended` paketi; planlama (`cx:plan`), test stratejisi (`cx:test`) ve dokümantasyon (`cx:doc`) gibi ek komutlar içerir. `ops` paketi ise dağıtım (`cx:deploy`), rollback (`cx:rollback`) ve operasyonel durum raporları (`cx:status`) sağlar. Paket kurulduğunda `.codexpp/commands/<paket>.toml` dosyaları oluşturulur ve `commands list` komutuyla otomatik olarak görünür.

### Codex CLI Entegrasyonu

Codexpp, Codex CLI ile çalışmayı kolaylaştıran iki yardımcı komut sağlar:

```bash
codexpp codex status              # Codex ikilisini ve AGENTS.md durumunu kontrol eder
codexpp codex setup --force       # Persona yönergelerini proje ve ~/.codex/AGENTS.md dosyalarına yazar
codexpp codex install --include-pack extended --force
codexpp codex init --profile full --force    # Bootstrap + persona + extended/ops paketleri
```

Codex CLI ile entegrasyon için örnek akış:

1. `codexpp codex status` ile Codex ikilisinin PATH'te olup olmadığını ve persona dosyalarının mevcut durumunu kontrol edin.
2. Yeni bir projede başlıyorsanız `codexpp codex init --profile full` komutu bootstrap klasörlerini, persona senkronizasyonunu ve `extended` / `ops` paketlerini otomatik kurar.
3. Halihazırdaki bir projede yalnızca komutları Codex CLI'ya eklemek isterseniz `codexpp codex install --include-pack extended --include-pack ops` çalıştırın. Bu komut `~/.codex/config.toml` içerisindeki eski `slash_commands` bloklarını temizleyip yeni `/prompts:cx-*` girdilerini ekler, gerekli Markdown prompt dosyalarını `~/.codex/prompts/` dizinine yazar ve varsayılan MCP paketini kurup profilleri `~/.codex/mcp/` dizinine senkronize eder.
4. Codex CLI'yi (`codex`) başlatıp `/prompts:` menüsüne girdiğinizde `cx:*` komutlarının listelendiğini görmelisiniz. Her komut, README'deki argument ipuçlarını `?` kısayoluyla gösterir.
5. Komutları programatik olarak tetiklemek için istediğiniz dizinde `codexpp commands run <kimlik> --exec` çağrısı yapabilir, gerekiyorsa `--codex-arg` bayrakları ile Codex CLI'ya ek parametreler geçebilirsiniz.

`codexpp commands run <kimlik> --exec` çağrıları arka planda `codex exec` çalıştırır; isterseniz `--summary-format` parametresiyle planı JSON/Markdown olarak kaydedip sonra Codex CLI’ya yapıştırabilirsiniz.

`codexpp codex install`, projede tanımlı tüm komutları Codex config dosyasına (`~/.codex/config.toml`) slash komutu olarak işler, `~/.codex/prompts/` dizinine YAML frontmatter’lı prompt dosyaları oluşturur ve varsayılan MCP paketini kurup profilleri `~/.codex/mcp/` dizinine senkronize eder. `--include-pack extended` gibi bayraklarla yerleşik paketler eklenebilir; komutlar Codex oturumunda `/prompts:cx-plan`, `/prompts:cx-test` vb. şeklinde doğrudan seçilebilir hale gelir. `codex init` komutu ise bootstrap + persona senkronizasyonu + paket kurulumu adımlarını tek seferde tamamlar.

### MCP Profilleri

`codexpp`, Codex CLI ile birlikte Model Context Protocol (MCP) sunucularını da yönetebilir. Yerleşik `default` paketi şu MCP sunucularını içerir:

- **Filesystem** - Dosya sistemi işlemleri (auto-start)
- **Context7** - Güncel kütüphane dokümantasyonları (auto-start)
- **GitHub** - Repository ve issue yönetimi
- **Memory** - Proje bağlamını hatırlama
- **Sequential Thinking** - Karmaşık problem çözme
- **Puppeteer** - Web tarayıcı otomasyonu

```bash
codexpp mcp packs list
codexpp mcp packs install default --force      # Proje .codexpp/mcp/default.toml oluşturur
codexpp mcp list --verbose                     # Yüklü profillerin komut ve env bilgilerini göster
codexpp mcp setup --codex-dir ~/.codex/mcp \
  --format both --force --show-diff            # ~/.codex/mcp/*.{json,toml} dosyalarını yazar
```

`codex init --profile full` veya `codexpp codex install --force`, MCP profillerini otomatik kurar ve `~/.codex/config.toml` dosyasına ekler. `github` profili için `GITHUB_TOKEN` ortam değişkenini tanımlamayı unutmayın.

**Not:** Codex CLI'de `/mcp` komutu çalıştırıldığında bazı sunucular için "Method not found" hatası görülebilir. Bu normal bir durumdur; çoğu MCP sunucusu `resources/list` metodunu desteklemez, bunun yerine **tools** (araçlar) sağlar. Sunucular çalışıyor ve tools üzerinden kullanılabilir (örneğin filesystem'in `list_directory`, context7'nin `get-library-docs`). Sadece Puppeteer gibi bazı sunucular hem resources hem de tools sağlar.

### Metin Arayüzü (TUI)

Terminalde hızlıca komut parametrelerini doldurmak için basit bir menüye ihtiyaç duyarsanız:

```bash
codexpp tui --exec
```

Komut listesi üzerinden seçim yapabilir, parametreleri giriş formu olarak doldurabilir, isteğe göre `codex exec` ile doğrudan gönderebilirsiniz (`--exec` olmadan sadece özet ve prompt gösterilir).

### Persona Çıktısı

Projede kullanılan persona yönergelerini `AGENTS.md` dosyasına aktarabilirsiniz:

 ```bash
 codexpp personas export --output AGENTS.md
 codexpp personas export --persona implementation-engineer --persona code-reviewer --output docs/agents.md
 codexpp personas export --output -   # stdout'a yazdırır
 ```

Varsayılan olarak hedef dosya zaten varsa üzerine yazılmaz; `--force` bayrağı ekleyerek güncelleyebilirsiniz.

### Codex Hafızası Senkronizasyonu

Persona yönergelerini hem proje dosyanıza hem de Codex CLI hafıza klasörüne tek komutla yazabilirsiniz:

```bash
codexpp personas sync --force
codexpp personas sync --force --show-diff
codexpp personas sync --force --show-diff --diff-color always
codexpp personas sync --persona system-architect --output docs/AGENTS.md --codex-output ~/.codex/custom/AGENTS.md
codexpp personas sync --codex-output -   # yalnızca proje dosyasını günceller
```

`--output` veya `--codex-output` argümanlarından birini `-` yaparak ilgili hedefi atlayabilirsiniz. `--show-diff` bayrağı mevcut dosya içeriği değişiyorsa küçük bir unified diff çıktısı üretir; `--diff-color auto|always|never` ile renklendirme modunu kontrol edebilirsiniz (varsayılan `auto`). İçerik zaten güncelse yalnızca bilgilendirme mesajı gösterilir.

## Yol Haritası

- [ ] Codex hafızasında sürüm karşılaştırması ve geri alma seçenekleri
- [ ] MCP sunucu profilleri için kurulum sihirbazı eklemek
- [ ] TUI (Terminal User Interface) geliştirmeleri
- [ ] Daha fazla komut paketi ve persona tanımları

## Katkıda Bulunma

Katkılara açığız! Önerilerinizi ve geri bildirimlerinizi paylaşmaktan çekinmeyin. Issue açabilir veya pull request gönderebilirsiniz.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

