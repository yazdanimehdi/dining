(function () {
    var bHeight, bWidth, block, bname, closeBtn, closeContent, content, expand, openContent, updateValues, wHeight,
        wWidth, xVal, yVal;

    block = $('.blocks__block');

    bname = $('.blocks__name');

    content = $('.blocks-content__content');

    closeBtn = $('.blocks__content-close');

    wHeight = $(window).outerHeight();

    wWidth = $(window).outerWidth();

    bHeight = block.outerHeight();

    bWidth = block.outerWidth();

    xVal = Math.round(wWidth / bWidth) + 0.03;

    yVal = wHeight / bHeight + 0.03;

    expand = function () {
        var aBlock, num;
        num = $(this).index();
        aBlock = block.eq(num);
        if (!aBlock.hasClass('active')) {
            bname.css('opacity', '0');
            aBlock.css({
                'transform': 'scale(' + xVal + ',' + yVal + ')',
                '-webkit-transform': 'scale(' + xVal + ',' + yVal + ')'
            });
            aBlock.addClass('active');
            openContent(num);
        }
    };

    openContent = function (num) {
        var aContent;
        content.css({
            'transition': 'all 0.3s 0.4s ease-out',
            '-webkit-transition': 'all 0.3s 0.4s ease-out'
        });
        aContent = content.eq(num);
        aContent.addClass('active');
    };

    closeContent = function () {
        bname.css('opacity', '1');
        content.css({
            'transition': 'all 0.1s 0 ease-out',
            '-webkit-transition': 'all 0.1s 0 ease-out'
        });
        block.css({
            'transform': 'scale(1)',
            '-webkit-transform': 'scale(1)'
        });
        block.removeClass('active');
        content.removeClass('active');
    };

    updateValues = function () {
        var yVal;
        var xVal;
        var bWidth;
        var bHeight;
        var wWidth;
        var wHeight;
        var aBlock;
        if (block.hasClass('active')) {
            aBlock = $('.blocks__block.active');
            wHeight = $(window).height();
            wWidth = $(window).width();
            bHeight = block.height();
            bWidth = block.width();
            xVal = Math.round(wWidth / bWidth) + 0.03;
            yVal = wHeight / bHeight + 0.03;
            aBlock.css({
                'transform': 'scale(' + xVal + ',' + yVal + ')',
                '-webkit-transform': 'scale(' + xVal + ',' + yVal + ')'
            });
        }
    };

    $(window).on('resize', updateValues);

    bname.on('click', expand);

    closeBtn.on('click', closeContent);

}).call(this);

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiPGFub255bW91cz4iXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUFBQSxNQUFBLE9BQUEsRUFBQSxNQUFBLEVBQUEsS0FBQSxFQUFBLEtBQUEsRUFBQSxRQUFBLEVBQUEsWUFBQSxFQUFBLE9BQUEsRUFBQSxNQUFBLEVBQUEsV0FBQSxFQUFBLFlBQUEsRUFBQSxPQUFBLEVBQUEsTUFBQSxFQUFBLElBQUEsRUFBQTs7RUFBQSxLQUFBLEdBQVEsQ0FBQSxDQUFFLGdCQUFGOztFQUNSLEtBQUEsR0FBUSxDQUFBLENBQUUsZUFBRjs7RUFDUixPQUFBLEdBQVUsQ0FBQSxDQUFFLDBCQUFGOztFQUNWLFFBQUEsR0FBVyxDQUFBLENBQUUsd0JBQUY7O0VBQ1gsT0FBQSxHQUFVLENBQUEsQ0FBRSxNQUFGLENBQVMsQ0FBQyxXQUFWLENBQUE7O0VBQ1YsTUFBQSxHQUFTLENBQUEsQ0FBRSxNQUFGLENBQVMsQ0FBQyxVQUFWLENBQUE7O0VBQ1QsT0FBQSxHQUFVLEtBQUssQ0FBQyxXQUFOLENBQUE7O0VBQ1YsTUFBQSxHQUFTLEtBQUssQ0FBQyxVQUFOLENBQUE7O0VBQ1QsSUFBQSxHQUFPLElBQUksQ0FBQyxLQUFMLENBQVcsTUFBQSxHQUFTLE1BQXBCLENBQUEsR0FBOEI7O0VBQ3JDLElBQUEsR0FBTyxPQUFBLEdBQVUsT0FBVixHQUFvQjs7RUFFM0IsTUFBQSxHQUFTLFFBQUEsQ0FBQSxDQUFBO0FBQ1AsUUFBQSxNQUFBLEVBQUE7SUFBQSxHQUFBLEdBQU0sQ0FBQSxDQUFFLElBQUYsQ0FBTyxDQUFDLEtBQVIsQ0FBQTtJQUNOLE1BQUEsR0FBUyxLQUFLLENBQUMsRUFBTixDQUFTLEdBQVQ7SUFDVCxJQUFHLENBQUMsTUFBTSxDQUFDLFFBQVAsQ0FBZ0IsUUFBaEIsQ0FBSjtNQUNFLEtBQUssQ0FBQyxHQUFOLENBQVUsU0FBVixFQUFxQixHQUFyQjtNQUNBLE1BQU0sQ0FBQyxHQUFQLENBQ0U7UUFBQSxXQUFBLEVBQWEsUUFBQSxHQUFXLElBQVgsR0FBa0IsR0FBbEIsR0FBd0IsSUFBeEIsR0FBK0IsR0FBNUM7UUFDQSxtQkFBQSxFQUFxQixRQUFBLEdBQVcsSUFBWCxHQUFrQixHQUFsQixHQUF3QixJQUF4QixHQUErQjtNQURwRCxDQURGO01BR0EsTUFBTSxDQUFDLFFBQVAsQ0FBZ0IsUUFBaEI7TUFDQSxXQUFBLENBQVksR0FBWixFQU5GOztFQUhPOztFQVlULFdBQUEsR0FBYyxRQUFBLENBQUMsR0FBRCxDQUFBO0FBQ1osUUFBQTtJQUFBLE9BQU8sQ0FBQyxHQUFSLENBQ0U7TUFBQSxZQUFBLEVBQWMsd0JBQWQ7TUFDQSxvQkFBQSxFQUFzQjtJQUR0QixDQURGO0lBR0EsUUFBQSxHQUFXLE9BQU8sQ0FBQyxFQUFSLENBQVcsR0FBWDtJQUNYLFFBQVEsQ0FBQyxRQUFULENBQWtCLFFBQWxCO0VBTFk7O0VBUWQsWUFBQSxHQUFlLFFBQUEsQ0FBQSxDQUFBO0lBQ2IsS0FBSyxDQUFDLEdBQU4sQ0FBVSxTQUFWLEVBQXFCLEdBQXJCO0lBQ0EsT0FBTyxDQUFDLEdBQVIsQ0FDRTtNQUFBLFlBQUEsRUFBYyxxQkFBZDtNQUNBLG9CQUFBLEVBQXNCO0lBRHRCLENBREY7SUFHQSxLQUFLLENBQUMsR0FBTixDQUNFO01BQUEsV0FBQSxFQUFhLFVBQWI7TUFDQSxtQkFBQSxFQUFxQjtJQURyQixDQURGO0lBR0EsS0FBSyxDQUFDLFdBQU4sQ0FBa0IsUUFBbEI7SUFDQSxPQUFPLENBQUMsV0FBUixDQUFvQixRQUFwQjtFQVRhOztFQVlmLFlBQUEsR0FBZSxRQUFBLENBQUEsQ0FBQTtJQUNiO0lBQ0E7SUFDQTtJQUNBO0lBQ0E7SUFDQTtBQUxBLFFBQUE7SUFNQSxJQUFHLEtBQUssQ0FBQyxRQUFOLENBQWUsUUFBZixDQUFIO01BQ0UsTUFBQSxHQUFTLENBQUEsQ0FBRSx1QkFBRjtNQUNULE9BQUEsR0FBVSxDQUFBLENBQUUsTUFBRixDQUFTLENBQUMsTUFBVixDQUFBO01BQ1YsTUFBQSxHQUFTLENBQUEsQ0FBRSxNQUFGLENBQVMsQ0FBQyxLQUFWLENBQUE7TUFDVCxPQUFBLEdBQVUsS0FBSyxDQUFDLE1BQU4sQ0FBQTtNQUNWLE1BQUEsR0FBUyxLQUFLLENBQUMsS0FBTixDQUFBO01BQ1QsSUFBQSxHQUFPLElBQUksQ0FBQyxLQUFMLENBQVcsTUFBQSxHQUFTLE1BQXBCLENBQUEsR0FBOEI7TUFDckMsSUFBQSxHQUFPLE9BQUEsR0FBVSxPQUFWLEdBQW9CO01BQzNCLE1BQU0sQ0FBQyxHQUFQLENBQ0U7UUFBQSxXQUFBLEVBQWEsUUFBQSxHQUFXLElBQVgsR0FBa0IsR0FBbEIsR0FBd0IsSUFBeEIsR0FBK0IsR0FBNUM7UUFDQSxtQkFBQSxFQUFxQixRQUFBLEdBQVcsSUFBWCxHQUFrQixHQUFsQixHQUF3QixJQUF4QixHQUErQjtNQURwRCxDQURGLEVBUkY7O0VBUGE7O0VBb0JmLENBQUEsQ0FBRSxNQUFGLENBQVMsQ0FBQyxFQUFWLENBQWEsUUFBYixFQUF1QixZQUF2Qjs7RUFDQSxLQUFLLENBQUMsRUFBTixDQUFTLE9BQVQsRUFBa0IsTUFBbEI7O0VBQ0EsUUFBUSxDQUFDLEVBQVQsQ0FBWSxPQUFaLEVBQXFCLFlBQXJCO0FBakVBIiwic291cmNlc0NvbnRlbnQiOlsiYmxvY2sgPSAkKCcuYmxvY2tzX19ibG9jaycpXG5ibmFtZSA9ICQoJy5ibG9ja3NfX25hbWUnKVxuY29udGVudCA9ICQoJy5ibG9ja3MtY29udGVudF9fY29udGVudCcpXG5jbG9zZUJ0biA9ICQoJy5ibG9ja3NfX2NvbnRlbnQtY2xvc2UnKVxud0hlaWdodCA9ICQod2luZG93KS5vdXRlckhlaWdodCgpXG53V2lkdGggPSAkKHdpbmRvdykub3V0ZXJXaWR0aCgpXG5iSGVpZ2h0ID0gYmxvY2sub3V0ZXJIZWlnaHQoKVxuYldpZHRoID0gYmxvY2sub3V0ZXJXaWR0aCgpXG54VmFsID0gTWF0aC5yb3VuZCh3V2lkdGggLyBiV2lkdGgpICsgMC4wM1xueVZhbCA9IHdIZWlnaHQgLyBiSGVpZ2h0ICsgMC4wM1xuXG5leHBhbmQgPSAtPlxuICBudW0gPSAkKHRoaXMpLmluZGV4KClcbiAgYUJsb2NrID0gYmxvY2suZXEobnVtKVxuICBpZiAhYUJsb2NrLmhhc0NsYXNzKCdhY3RpdmUnKVxuICAgIGJuYW1lLmNzcyAnb3BhY2l0eScsICcwJ1xuICAgIGFCbG9jay5jc3NcbiAgICAgICd0cmFuc2Zvcm0nOiAnc2NhbGUoJyArIHhWYWwgKyAnLCcgKyB5VmFsICsgJyknXG4gICAgICAnLXdlYmtpdC10cmFuc2Zvcm0nOiAnc2NhbGUoJyArIHhWYWwgKyAnLCcgKyB5VmFsICsgJyknXG4gICAgYUJsb2NrLmFkZENsYXNzICdhY3RpdmUnXG4gICAgb3BlbkNvbnRlbnQgbnVtXG4gIHJldHVyblxuXG5vcGVuQ29udGVudCA9IChudW0pIC0+XG4gIGNvbnRlbnQuY3NzXG4gICAgJ3RyYW5zaXRpb24nOiAnYWxsIDAuM3MgMC40cyBlYXNlLW91dCdcbiAgICAnLXdlYmtpdC10cmFuc2l0aW9uJzogJ2FsbCAwLjNzIDAuNHMgZWFzZS1vdXQnXG4gIGFDb250ZW50ID0gY29udGVudC5lcShudW0pXG4gIGFDb250ZW50LmFkZENsYXNzICdhY3RpdmUnXG4gIHJldHVyblxuXG5jbG9zZUNvbnRlbnQgPSAtPlxuICBibmFtZS5jc3MgJ29wYWNpdHknLCAnMSdcbiAgY29udGVudC5jc3NcbiAgICAndHJhbnNpdGlvbic6ICdhbGwgMC4xcyAwIGVhc2Utb3V0J1xuICAgICctd2Via2l0LXRyYW5zaXRpb24nOiAnYWxsIDAuMXMgMCBlYXNlLW91dCdcbiAgYmxvY2suY3NzXG4gICAgJ3RyYW5zZm9ybSc6ICdzY2FsZSgxKSdcbiAgICAnLXdlYmtpdC10cmFuc2Zvcm0nOiAnc2NhbGUoMSknXG4gIGJsb2NrLnJlbW92ZUNsYXNzICdhY3RpdmUnXG4gIGNvbnRlbnQucmVtb3ZlQ2xhc3MgJ2FjdGl2ZSdcbiAgcmV0dXJuXG5cbnVwZGF0ZVZhbHVlcyA9IC0+XG4gIGB2YXIgeVZhbGBcbiAgYHZhciB4VmFsYFxuICBgdmFyIGJXaWR0aGBcbiAgYHZhciBiSGVpZ2h0YFxuICBgdmFyIHdXaWR0aGBcbiAgYHZhciB3SGVpZ2h0YFxuICBpZiBibG9jay5oYXNDbGFzcygnYWN0aXZlJylcbiAgICBhQmxvY2sgPSAkKCcuYmxvY2tzX19ibG9jay5hY3RpdmUnKVxuICAgIHdIZWlnaHQgPSAkKHdpbmRvdykuaGVpZ2h0KClcbiAgICB3V2lkdGggPSAkKHdpbmRvdykud2lkdGgoKVxuICAgIGJIZWlnaHQgPSBibG9jay5oZWlnaHQoKVxuICAgIGJXaWR0aCA9IGJsb2NrLndpZHRoKClcbiAgICB4VmFsID0gTWF0aC5yb3VuZCh3V2lkdGggLyBiV2lkdGgpICsgMC4wM1xuICAgIHlWYWwgPSB3SGVpZ2h0IC8gYkhlaWdodCArIDAuMDNcbiAgICBhQmxvY2suY3NzXG4gICAgICAndHJhbnNmb3JtJzogJ3NjYWxlKCcgKyB4VmFsICsgJywnICsgeVZhbCArICcpJ1xuICAgICAgJy13ZWJraXQtdHJhbnNmb3JtJzogJ3NjYWxlKCcgKyB4VmFsICsgJywnICsgeVZhbCArICcpJ1xuICByZXR1cm5cblxuJCh3aW5kb3cpLm9uICdyZXNpemUnLCB1cGRhdGVWYWx1ZXNcbmJuYW1lLm9uICdjbGljaycsIGV4cGFuZFxuY2xvc2VCdG4ub24gJ2NsaWNrJywgY2xvc2VDb250ZW50Il19
//# sourceURL=coffeescript