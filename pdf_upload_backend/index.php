<?php
if(!hash_equals('PLEASE_FILL_IN_SOME_READ_SECRET', $_GET['secret']))
{
	header('HTTP/1.1 403 Access denied');
	die('Access denied');
}

//make sure everything gets properly refreshed
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
if(isset($_GET['id']) && is_numeric($_GET['id']))
{
	$filename = "{$_GET['id']}.pdf";
	if(!file_exists($filename))
	{
		header('HTTP/1.1 404 Not Found');
		die('Not Found');
	}
	$fp = fopen($filename, 'rb');
	header("Content-Type: application/octet-stream");
	header("Content-Length: ".filesize($filename));
	fpassthru($fp);
	exit;
}
?><!DOCTYPE html>
<html>
	<head>
		<script src="/pdfjs/build/pdf.js"></script>
		<script>
			"use strict";
			const scale = 1.0;
			pdfjsLib.GlobalWorkerOptions.workerSrc = "/pdfjs/build/pdf.worker.js";
			const loader = async (id) => {
				try {
					const loadingTask = pdfjsLib.getDocument("/index.php?secret=<?=$_GET['secret']?>&id="+id+"&time="+Date.now());
					const pdf = await loadingTask.promise;
					
					//
					// Fetch the first page
					//
					const page = await pdf.getPage(1);
					const viewport = page.getViewport({ scale });
					// Support HiDPI-screens.
					const outputScale = window.devicePixelRatio || 1;

					//
					// Prepare canvas using PDF page dimensions
					//
					const canvas = document.getElementById("canvas-"+id);
					const context = canvas.getContext("2d");

					canvas.width = Math.floor(viewport.width * outputScale);
					canvas.height = Math.floor(viewport.height * outputScale);

					const transform = outputScale !== 1  ? [outputScale, 0, 0, outputScale, 0, 0] : null;

					//
					// Render PDF page into canvas context
					//
					const renderContext = {
						canvasContext: context,
						transform,
						viewport,
					};
					page.render(renderContext);
					
					return canvas;
				} catch {
					return null;
				}
			};
			
			window.addEventListener("DOMContentLoaded", async (event) => {
				//load all pages
				let i = 0;
				let pages = [];
				do {
					console.log("loading pdf "+(i+1));
					let page = await loader(i+1);
					if(page !== null)
						pages.push(page);
					i++;
				} while(i < 4);
				console.log("every pdf loaded...");
				
				//flip pages every 20 seconds
				i = pages.length - 1;
				let looper = () => {
					let old_canvas = pages[i];
					i++;
					if(i >= pages.length)
						i = 0;
					let canvas = pages[i];
					old_canvas.style.display = "none";
					canvas.style.display = "block";
					console.log("flipping to: ", i, canvas);
				};
				looper();
				window.setInterval(looper, <?=isset($_GET['time']) ? (int)$_GET['time']*1000 : 20000?>);
			});
		</script>
		<style>
			body {
				position: absolute;
				width: calc(100% - 1em);
				height: 100%;
				margin-top: -0.251em;
				display: flex;
				justify-content: center;
			}
			.canvas {
				display: none;
				position: absolute;
				width: auto;
				height: auto;
				max-width: 100%;
				max-height: 100%;
				margin: auto;
				direction: ltr;
			}
		</style>
	</head>
	<body>
		<h3>Lade Daten...</h3>
		<canvas id="canvas-1" class="canvas"></canvas>
		<canvas id="canvas-2" class="canvas"></canvas>
		<canvas id="canvas-3" class="canvas"></canvas>
		<canvas id="canvas-4" class="canvas"></canvas>
	</body>
</html>