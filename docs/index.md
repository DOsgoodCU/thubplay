<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); /* Smaller boxes */
        gap: 5px;
        justify-content: center;
        padding: 5px;
    }

    .iframe-wrapper {
        position: relative;
        width: 400px;  /* Smrller box size */
        height: 400px; /* Adjusted height */
        overflow: hidden;
        display: inline-block;
        border: 1px solid black;
        border-radius: 8px; /* Optional: Rounded corners */
        text-align: center;
    }

    .iframe-wrapper iframe {
        width: 2000px;  /* Adjusted larger size for scaling */
        height: 1000px; /* Adjusted height */
        transform: scale(0.5); /* Keep scaling */ 
	transform-origin: top left;
    }

    .clickable-overlay {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: 10;
    }

    .iframe-title {
        position: absolute;
        top: 0px; /* Title above the iframe */
        width: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        text-align: center;
        padding: 5px;
        font-size: 16px;
        z-index: 15;
    }

    /* Optional: Hover effect */
    .iframe-wrapper:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: box-shadow 0.3s ease-in-out;
    }
</style>

<div class="grid-container">
    <!-- Ethiopia OND iframe -->
    <div class="iframe-wrapper">
        <div class="iframe-title">Ethiopia OND</div>
        <a href="https://fist.iri.columbia.edu/publications/docs/ethiopia_aa_dashboard_somali_ond/" target="_blank" class="clickable-overlay"></a>
        <iframe src="https://fist.iri.columbia.edu/publications/docs/ethiopia_aa_dashboard_somali_ond/"></iframe>
    </div>

    <!-- Madagascar OND iframe -->
    <div class="iframe-wrapper">
        <div class="iframe-title">Madagascar OND</div>
        <a href="https://fist.iri.columbia.edu/publications/docs/Madagascar_AA_FLexDashboard_OND_2024/" target="_blank" class="clickable-overlay"></a>
        <iframe src="https://fist.iri.columbia.edu/publications/docs/Madagascar_AA_FLexDashboard_OND_2024/"></iframe>
    </div>

    <!-- Niger iframe -->
    <div class="iframe-wrapper">
        <div class="iframe-title">Niger</div>
        <a href="https://fist.iri.columbia.edu/publications/docs/Niger_AA_FLexDashboard_simplified_JAS/" target="_blank" class="clickable-overlay"></a>
        <iframe src="https://fist.iri.columbia.edu/publications/docs/Niger_AA_FLexDashboard_simplified_JAS/"></iframe>
    </div>
</div>

