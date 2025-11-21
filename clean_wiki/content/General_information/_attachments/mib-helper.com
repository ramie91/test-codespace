<!doctype html>
<html lang="en">

<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>MIB-Helper.com - VAG Infotainment System toolset</title>
    <meta name="description" content="Find out if your Audi, VW, Seat, Skoda Infotainment System is MIB1 or MIB2" />

    <!--Google font-->
    <link href="https://fonts.googleapis.com/css?family=K2D:300,400,500,700,800" rel="stylesheet">

    <!-- Bootstrap CSS / Color Scheme -->
    <link rel="stylesheet" href="mib-helper/html/css/bootstrap.css">
    
    <!-- FontAwesome -->
    <link href="mib-helper/html/assets/fontawesome/css/all.css" rel="stylesheet">
    
    <!-- favicon -->
    <link rel="apple-touch-icon" sizes="57x57" href="mib-helper/html/favicon/apple-icon-57x57.png">
    <link rel="apple-touch-icon" sizes="60x60" href="mib-helper/html/favicon/apple-icon-60x60.png">
    <link rel="apple-touch-icon" sizes="72x72" href="mib-helper/html/favicon/apple-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="76x76" href="mib-helper/html/favicon/apple-icon-76x76.png">
    <link rel="apple-touch-icon" sizes="114x114" href="mib-helper/html/favicon/apple-icon-114x114.png">
    <link rel="apple-touch-icon" sizes="120x120" href="mib-helper/html/favicon/apple-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="144x144" href="mib-helper/html/favicon/apple-icon-144x144.png">
    <link rel="apple-touch-icon" sizes="152x152" href="mib-helper/html/favicon/apple-icon-152x152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="mib-helper/html/favicon/apple-icon-180x180.png">
    <link rel="icon" type="image/png" sizes="192x192"  href="mib-helper/html/favicon/android-icon-192x192.png">
    <link rel="icon" type="image/png" sizes="32x32" href="mib-helper/html/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="96x96" href="mib-helper/html/favicon/favicon-96x96.png">
    <link rel="icon" type="image/png" sizes="16x16" href="mib-helper/html/favicon/favicon-16x16.png">
    <link rel="manifest" href="mib-helper/html/favicon/manifest.json">
    <meta name="msapplication-TileColor" content="#ffd401">
    <meta name="msapplication-TileImage" content="mib-helper/html/favicon/ms-icon-144x144.png">
    <meta name="theme-color" content="#ffd401">
    <meta name="apple-mobile-web-app-title" content="MIB-Helper">
    
    <!-- og -->
    <meta property="og:url" content="http://mib-helper.com/" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="MIB-Helper.com - VAG Infotainment System toolset" />
    <meta property="og:description" content="Check VAG Infotainment System details" />
    <meta property="og:image" content="http://mib-helper.com/html/favicon/android-icon-192x192.png" />
    <meta property="og:image:alt" content="MIB-Helper logo" />
</head>

<body>

  <!--Header Section-->
  <section class="bg-gradient pt-5 pb-6">
    <div class="container">
      <div class="row">
        <div class="col-12 d-flex flex-row align-items-center justify-content-between">
          <a href="https://mib-helper.com/"><div class="heading-brand">MIB-Helper.com</div></a>
        </div>
        <div class="col-12">
            <ul class="list-inline topMenu">
                <li class="list-inline-item"><a href="https://mib-helper.com/show.php?all=maps">Maps</a></li><li class="list-inline-item"><a href="https://mib-helper.com/what-the-mib/">What The MIB</a></li><li class="list-inline-item"><a href="https://mib-helper.com/im-so-xory/">I'm So XORy</a></li><li class="list-inline-item"><a href="https://mib-helper.com/fec-decoder/">FEC Decoder</a></li>
            </ul>  
        </div>
      </div>
      <div class="row mt-6">
        <div class="col-md-8 mx-auto text-center">
          <h1>ENTER SW TRAIN</h1>
          <p class="lead mb-5">Find it in system settings or hidden service menu.</p>

          <form action="index.php#details">
              <div class="form-group">
                <input type="text" class="form-control form-control-lg" id="partNumber" aria-describedby="partNumberHelp" placeholder="example: MST2_EU_VW_ZR_P0480T" name="train" value="">
              </div>
              <button type="submit" class="btn btn-success">Go!</button>
          </form>

        </div>
      </div>

      <a name="details"></a>
      <div class="row mt-5">
        <div class="col-md-9 mx-auto">
          <div class="code-window">
            <div class="dots">
              <div class="red"></div>
              <div class="orange"></div>
              <div class="green"></div>
            </div>
            <pre class="language-json line-numbers"><code class="language-json">Loading tool... 
Loaded <b>MIB-Helper v0.12.1 public beta</b>
This version is available in English language only.

Please provide SW Train above.

This version can:
<i class="fa-regular fa-square-check"></i> decode SW Train details;
<i class="fa-regular fa-square-check"></i> find latest available firmware updates, navigation maps;
<i class="fa-regular fa-square-check"></i> find latest RadioStation DB logos, Personal POI packages;
<i class="fa-regular fa-square-check"></i> find activation methods and VIM unlock methods;
<i class="fa-regular fa-square-check"></i> find MIB related software, hardware tools, retrofit kits.

Popular SW Trains:
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MSTD_EU_VW_P5301"><u>MSTD_EU_VW_P5301</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MSTD_EU_SK_P6230"><u>MSTD_EU_SK_P6230</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MSTD_EU_AU_P5101"><u>MSTD_EU_AU_P5101</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MSTD_EU_SE_P3311"><u>MSTD_EU_SE_P3311</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHIG_EU_VW_K1550"><u>MHIG_EU_VW_K1550</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHIG_EU_SK_K1552"><u>MHIG_EU_SK_K1552</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHIG_EU_AU_K1555"><u>MHIG_EU_AU_K1555</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MST2_EU_VW_ZR_P0254T"><u>MST2_EU_VW_ZR_P0254T</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MST2_EU_VW_ZR_P0480T"><u>MST2_EU_VW_ZR_P0480T</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MST2_EU_SK_PQ_P0253T"><u>MST2_EU_SK_PQ_P0253T</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MST2_EU_VW_P0231D"><u>MST2_EU_VW_P0231D</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MST2_EU_VW_P0879D"><u>MST2_EU_VW_P0879D</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MST2_EU_AU_P0965D"><u>MST2_EU_AU_P0965D</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_AU37X_P5089"><u>MHI2_ER_AU37X_P5089</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_AUG11_P0040"><u>MHI2_ER_AUG11_P0040</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_AU57X_K3663"><u>MHI2_ER_AU57X_K3663</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_VWG11_K3342"><u>MHI2_ER_VWG11_K3342</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_VWG13_K4525"><u>MHI2_ER_VWG13_K4525</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_SEG11_P4709"><u>MHI2_ER_SEG11_P4709</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_SKG11_K3343"><u>MHI2_ER_SKG11_K3343</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2_ER_SKG13_P4526"><u>MHI2_ER_SKG13_P4526</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHS2_ER_AU_P2035"><u>MHS2_ER_AU_P2035</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MH2P_US_POG35_P9829"><u>MH2P_US_POG35_P9829</u></a>
<i class="fa-regular fa-file-zipper"></i> <a href="index.php?train=MHI2Q_ER_AUG22_P5092"><u>MHI2Q_ER_AUG22_P5092</u></a>
<i class="fa-solid fa-circle-info" style="color: #FFAA00"></i> Check all firmwares <a href="show.php?all=firmwares#details"><u>here</u></a>.

<i class="fa-solid fa-heart"></i> Huge thanks to MIB community members for sharing their knownledge!
<i class="fa-brands fa-youtube"></i> Subscribe to the <a href="https://www.youtube.com/channel/UCS_b_hdTBvgm3-yXU-K8JPA" target="_blank"><u>official MIB Helper YouTube Channel</u></a>.

<i class="fa-solid fa-triangle-exclamation" style="color: #FF0000"></i> Anything you do with your MIB, you do at your own risk.
<i class="fa-solid fa-circle-info" style="color: #FFAA00"></i> This website only links to external sources.
<i class="fa-solid fa-circle-info" style="color: #FFAA00"></i> We are not hosting firmwares, updates, maps, toolboxes, etc.

MIB-Helper v0.12.1 public beta finished. Bye!</code></pre>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!--footer-->
  <footer class="py-5 bg-light">
    <div class="container">
      <div class="row">
        <div class="col-12 text-center">
            <ul class="list-inline">
            <li class="list-inline-item"><a href="https://mib-helper.com/show.php?all=maps">Maps</a></li><li class="list-inline-item"><a href="https://mib-helper.com/what-the-mib/">What The MIB</a></li><li class="list-inline-item"><a href="https://mib-helper.com/im-so-xory/">I'm So XORy</a></li><li class="list-inline-item"><a href="https://mib-helper.com/fec-decoder/">FEC Decoder</a></li>
          </ul>
          <ul class="list-inline">
            <li class="list-inline-item"><a href="https://www.youtube.com/mrfixpl" target="_blank">mr-fix</a></li><li class="list-inline-item"><a href="https://ilovecarmods.com/" target="_blank">iLoveCarMods.com</a></li><li class="list-inline-item"><a href="https://mibwiki.one" target="_blank">mibwiki.one</a></li><li class="list-inline-item"><a href="https://mibsolution.one" target="_blank">mibsolution.one</a></li>
          </ul>
        </div>
      </div>
      <div class="row my-2">
        <div class="col-md-4 mx-auto text-muted text-center small-xl">
          &copy; 2019 Prism - All Rights Reserved
        </div>
      </div>
    </div>
  </footer>

    <!-- jQuery first, then Popper.js, then Bootstrap JS, then AdSense -->
    <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.7.3/feather.min.js"></script>
    <script src="mib-helper/html/js/scripts.js"></script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9956453308137419" crossorigin="anonymous"></script>
</body>

</html>
