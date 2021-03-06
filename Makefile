.PHONY: all
.SECONDARY:

all: data/output/replayed_links_to_restore.csv data/output/replayed_links_to_delete.csv

data/tatoeba/%.tar.bz2:
	wget --timestamping --directory-prefix=data/tatoeba/ \
		http://downloads.tatoeba.org/exports/$*.tar.bz2

data/tatoeba/%.csv: data/tatoeba/%.tar.bz2
	tar --directory=data/tatoeba/ --extract --bzip2 --touch --file=$<

data/tatoeba/sentence_comments.csv: data/tatoeba/comments.tar.bz2
	tar --directory=data/tatoeba/ --extract --bzip2 --touch --file=$<

data/output/:
	mkdir -p data/output/

data/output/horus_redirects.csv: data/tatoeba/sentence_comments.csv data/output/
	grep -e '^\S*\s\S*\sHorus\s.*Please go to' $< \
		| sed -e 's/^\S*\s\(\S*\)\s\S*\s\S*\s\S*\sPlease go to #\([0-9]*\)\..*$$/\1\t\2/' \
		| grep -ve '^\([0-9]*\)\s\1$$' \
		| sort -k1b,1 \
		> $@

data/output/ids_in_%.csv: data/tatoeba/%.csv data/output/
	cut -f1 $< | sort -k1b,1 -u > $@

data/output/linked_ghosts.csv: data/output/ids_in_links.csv data/output/ids_in_sentences.csv
	comm -23 $^ > $@

data/output/ghost_redirects.csv: data/output/linked_ghosts.csv data/output/horus_redirects.csv
	join -j 1 $^ > $@

data/output/ghost_link_redirection.csv: data/output/ghost_redirects.csv data/tatoeba/links.csv
	sort data/tatoeba/links.csv -k1b,1 | join -j 1 $< - > $@

data/output/original_ghost_links.csv: data/output/ghost_link_redirection.csv
	cut -d' ' -f1,3 $< > $@

data/output/fixed_ghost_links.csv: data/output/ghost_link_redirection.csv
	cut -d' ' -f2,3 $< > $@

data/output/replay.sqlite \
    data/output/replayed_links_present.csv \
    data/output/replayed_links_deleted.csv \
    data/output/replayed_sentences_present.csv \
    data/output/replayed_sentences_deleted.csv: data/tatoeba/contributions_20181127.csv data/output/
	./replay_contributions.py $<

data/output/replayed_links_to_delete.csv: data/output/replayed_links_deleted.csv data/tatoeba/links.csv
	./tupleset.py and $^ > $@

data/output/replayed_links_to_restore.csv: data/output/replayed_links_present.csv data/tatoeba/links.csv
	./tupleset.py gt $^ > $@

data/output/rehydrated.sqlite: data/tatoeba/sentences.csv data/tatoeba/links.csv data/output/
	./rehydrate.py
