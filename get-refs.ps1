# Downloads the full-resolution reference photos of Málaga Towers into refs\full
# Run with GET-REFS.bat (double-click) or:  powershell -ExecutionPolicy Bypass -File get-refs.ps1
$ErrorActionPreference = 'Continue'
$dir = Join-Path $PSScriptRoot 'refs\full'
New-Item -ItemType Directory -Force $dir | Out-Null

$list = @(
  @('01_render_hero_lamela.jpg',              'https://www.lamela.com/wp-content/uploads/2019/07/00_MalagaTowers-scaled.jpg'),
  @('02_detail_white_plates_lamela.jpg',      'https://www.lamela.com/wp-content/uploads/2019/07/01_MalagaTowers-scaled.jpg'),
  @('03_detail_corner_stack_lamela.jpg',      'https://www.lamela.com/wp-content/uploads/2025/02/02a_MalagaTowers.jpg'),
  @('04_detail_corner_up_lamela.jpg',         'https://www.lamela.com/wp-content/uploads/2025/02/02b_MalagaTowers.jpg'),
  @('05_entrance_fins_lamela.jpg',            'https://www.lamela.com/wp-content/uploads/2025/02/03_MalagaTowers-scaled.jpg'),
  @('06_terrace_sea_view_lamela.jpg',         'https://www.lamela.com/wp-content/uploads/2025/02/04_MalagaTowers-scaled.jpg'),
  @('07_rooftop_pool_day_lamela.jpg',         'https://www.lamela.com/wp-content/uploads/2025/02/05_MalagaTowers-scaled.jpg'),
  @('08_rooftop_pool_sunset_lamela.jpg',      'https://www.lamela.com/wp-content/uploads/2025/02/06_MalagaTowers-scaled.jpg'),
  @('09_rooftop_pool_dusk_lamela.jpg',        'https://www.lamela.com/wp-content/uploads/2025/02/07_MalagaTowers-scaled.jpg'),
  @('10_lobby_lamela.jpg',                    'https://www.lamela.com/wp-content/uploads/2025/02/08_MalagaTowers-scaled.jpg'),
  @('11_photo_two_towers_commons.jpg',        'https://commons.wikimedia.org/wiki/Special:FilePath/M%C3%A1laga_Towers_20240716_104637.jpg'),
  @('12_photo_facade_up_commons.jpg',         'https://commons.wikimedia.org/wiki/Special:FilePath/M%C3%A1laga_Towers_20240716_104842.jpg'),
  @('13_photo_from_beach_commons.jpg',        'https://commons.wikimedia.org/wiki/Special:FilePath/M%C3%A1laga_Towers_20240716_105040.jpg'),
  @('14_render_aerial_promenade_idealista.jpg','https://st3.idealista.com/news/archivos/styles/fullwidth_xl/public/2022-11/images/malagatowers.jpg'),
  @('15_photo_park_vidaeconomica.jpg',        'https://www.vidaeconomica.com/wp-content/uploads/2024/02/Torre-Living-3-002.jpg'),
  @('16_photo_street_vidaeconomica.jpg',      'https://www.vidaeconomica.com/wp-content/uploads/2024/04/401A6096.jpg'),
  @('17_photo_chimney_and_towers_laopinion.jpg','https://estaticos-cdn.prensaiberica.es/clip/0f15de63-5684-495b-98c1-4e513408c9ca_alta-libre-aspect-ratio_default_0.jpg'),
  @('18_photo_in_fog_elespanol.jpg',          'https://s1.eestatic.com/2023/04/27/malaga/vivir/759434228_232728862_1706x960.jpg'),
  @('19_photo_promenade_aluman.jpg',          'https://www.grupoaluman.com/wp-content/uploads/2025/06/IMG_20230827_092445.jpg-1.jpg'),
  @('20_detail_plates_from_below_aluman.jpg', 'https://www.grupoaluman.com/wp-content/uploads/2025/06/XPJRRZDF2FBAXPL3ENTHA3P6NY-853x1024.jpg'),
  @('21_render_competition_lamela.jpg',       'https://www.lamela.com/wp-content/uploads/2019/07/Torres-del-R%C3%ADo-1.jpg')
)

$ok = 0
foreach ($i in $list) {
  $out = Join-Path $dir $i[0]
  try {
    Invoke-WebRequest -Uri $i[1] -OutFile $out -UserAgent 'Mozilla/5.0' -UseBasicParsing -MaximumRedirection 5
    Write-Host "OK    $($i[0])" -ForegroundColor Green; $ok++
  } catch {
    Write-Host "FAIL  $($i[0])  ($($i[1]))" -ForegroundColor Yellow
  }
}
Write-Host "`n$ok / $($list.Count) downloaded to $dir"
