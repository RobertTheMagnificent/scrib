<?php 
include( 'rss_php.php' );

function objToArr( $junk ) {
	$array = array();
	foreach( $junk as $key=>$value ) {
		if( is_array( $value ) ) $array[$key] = objToArr( $value );
		else if( is_object( $value ) ) $array[$key] = objToArr( $value );
		else $array[$key] = $value;
	}
	return $array;
}

$rss = new rss_php;
$rss->load( 'http://boards.4chan.org/soc/index.rss' );
$stuff = objToArr( $rss );
$num = count( $stuff['items'] );
$i=0;

while( $i < $num ) {
	$yik = $stuff['items'][$i]['description']['value'];
	if( !empty( $yik ) && $yik !== '' ) {twitter.com
		echo html_entity_decode( strip_tags( $yik ) ) . "\n";
		$i++;
	}
}

?>
