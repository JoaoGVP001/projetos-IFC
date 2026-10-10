import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';

enum ButtonVariant { primary, secondary, text, icon }

class CustomButton extends StatelessWidget {
  final String? label;
  final IconData? icon;
  final VoidCallback? onPressed;
  final ButtonVariant variant;
  final bool isLoading;
  final bool isFullWidth;
  final EdgeInsets? padding;
  final Color? backgroundColor;
  final Color? foregroundColor;

  const CustomButton({
    super.key,
    this.label,
    this.icon,
    required this.onPressed,
    this.variant = ButtonVariant.primary,
    this.isLoading = false,
    this.isFullWidth = false,
    this.padding,
    this.backgroundColor,
    this.foregroundColor,
  }) : assert(label != null || icon != null);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDisabled = onPressed == null || isLoading;

    Widget child;
    ButtonStyle? style;

    switch (variant) {
      case ButtonVariant.primary:
        child = _buildPrimaryChild(context);
        style = _buildPrimaryStyle(context, isDisabled);
        break;
      case ButtonVariant.secondary:
        child = _buildSecondaryChild(context);
        style = _buildSecondaryStyle(context, isDisabled);
        break;
      case ButtonVariant.text:
        child = _buildTextChild(context);
        style = _buildTextStyle(context, isDisabled);
        break;
      case ButtonVariant.icon:
        return IconButton(
          icon: isLoading
              ? SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      foregroundColor ?? theme.colorScheme.onSurface,
                    ),
                  ),
                )
              : Icon(icon),
          onPressed: isDisabled ? null : onPressed,
          tooltip: label,
        );
    }

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      child: ElevatedButton(
        onPressed: isDisabled ? null : onPressed,
        style: style,
        child: child,
      ),
    );
  }

  Widget _buildPrimaryChild(BuildContext context) {
    if (isLoading) {
      return SizedBox(
        height: 20,
        width: 20,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(
            foregroundColor ?? Colors.white,
          ),
        ),
      );
    }

    if (icon != null && label != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Text(label!),
        ],
      );
    }

    return Text(label ?? '');
  }

  Widget _buildSecondaryChild(BuildContext context) {
    return _buildPrimaryChild(context);
  }

  Widget _buildTextChild(BuildContext context) {
    if (isLoading) {
      return SizedBox(
        height: 20,
        width: 20,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(
            foregroundColor ?? Theme.of(context).colorScheme.primary,
          ),
        ),
      );
    }

    if (icon != null && label != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Text(label!),
        ],
      );
    }

    return Text(label ?? '');
  }

  ButtonStyle _buildPrimaryStyle(BuildContext context, bool isDisabled) {
    return ElevatedButton.styleFrom(
      backgroundColor: backgroundColor ?? AppColors.seed,
      foregroundColor: foregroundColor ?? Colors.white,
      padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: isDisabled ? 0 : 2,
      disabledBackgroundColor: AppColors.seed.withOpacity(0.5),
      disabledForegroundColor: Colors.white70,
    );
  }

  ButtonStyle _buildSecondaryStyle(BuildContext context, bool isDisabled) {
    return ElevatedButton.styleFrom(
      backgroundColor: backgroundColor ?? Colors.transparent,
      foregroundColor: foregroundColor ?? AppColors.seed,
      padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isDisabled
              ? AppColors.seed.withOpacity(0.3)
              : AppColors.seed,
          width: 2,
        ),
      ),
      elevation: 0,
    );
  }

  ButtonStyle _buildTextStyle(BuildContext context, bool isDisabled) {
    return TextButton.styleFrom(
      foregroundColor: foregroundColor ?? AppColors.seed,
      padding: padding ?? const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    );
  }
}

